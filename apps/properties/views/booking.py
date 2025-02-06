import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework import status

from apps.common.permission_class import RoleBasedPermission
from apps.common.views.api.generic import AppModelCUDAPIViewSet
from apps.properties.choices import RoleTypeChoices
from apps.properties.models.booking import Booking, Payment
from apps.properties.serializers.booking import BookingSerializer


class CreateRazorpayOrderView(AppModelCUDAPIViewSet):
    """Create a new Razor Pay Order view"""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.guest]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Override the create method for booking"""

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = self.get_user()
            property_id = serializer.validated_data["property"]
            room_type_id = serializer.validated_data["room_type"]
            joining_date = serializer.validated_data["joining_date"]
            amount = serializer.validated_data["amount"]
            booking = Booking.objects.create(
                user=user, property=property_id, room_type=room_type_id, joining_date=joining_date, status="pending"
            )
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            try:
                # This will create a order in razorpay this API is provided by the RAZORPAY
                # Once the order was created it will be saved in the Paymentlink

                razorpay_order = client.order.create(
                    {
                        "amount": int(amount * 100),
                        "currency": "INR",
                        "receipt": f"order_rcptid_{booking.id}",
                        "notes": {"booking_id": booking.id, "user_id": user.id},
                    }
                )
                if not razorpay_order:
                    return self.send_error_response(
                        {"error": "Razorpay Order creation failed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                ser_phone_number = str(user.phone_number)

                # Generate the payment link for the order
                # The user will be able to pay the booking amount by clicking on the payment link.
                # The payment details will be saved in the Payment table.
                # Once payment is done It will call the WEBHOOK

                payment_link = client.payment_link.create(
                    {
                        "amount": int(amount * 100),
                        "currency": "INR",
                        "accept_partial": False,
                        "description": "Booking Payment",
                        "customer": {
                            "email": user.email,
                            "contact": ser_phone_number,
                        },
                        "notify": {"sms": True, "email": True},
                        "reminder_enable": True,
                        "notes": {
                            "booking_id": booking.id,
                            "user_id": user.id,
                            "razorpay_order_id": razorpay_order["id"],
                        },
                    }
                )
                if not payment_link:
                    return self.send_error_response(
                        {"error": "Failed to generate payment link"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                Payment.objects.create(
                    booking=booking,
                    razorpay_payment_link_order_id=payment_link["id"],
                    razorpay_order_id=razorpay_order["id"],
                    amount=amount,
                )
                return self.send_response(
                    {
                        "message": "Payment link generated successfully",
                        "payment_link": payment_link["short_url"],
                        "order_id": booking.id,
                        "amount": amount,
                        "currency": "INR",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except razorpay.errors.BadRequestError as e:
                return self.send_error_response(
                    {"error": f"Razorpay Order creation failed: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return self.send_error_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
