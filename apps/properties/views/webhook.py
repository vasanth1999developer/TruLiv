import json

import razorpay
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.access.models.user import User
from apps.properties.choices import BookingStatusChoices, RoleTypeChoices
from apps.properties.models.booking import Payment
from apps.properties.utils import allocate_bed


@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(View):
    """Handles Razorpay webhook events."""

    def post(self, request, *args, **kwargs):
        """To handle Razorpay webhook events"""
        payload = request.body.decode("utf-8")
        signature = request.headers.get("X-Razorpay-Signature")
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_WEBHOOK_SECRET)
            data = json.loads(payload)
            payment_data = data.get("payload", {}).get("payment", {}).get("entity", {})
            razorpay_order_id = payment_data.get("notes", {}).get("razorpay_order_id")
            user_id = payment_data.get("notes", {}).get("user_id")
            razorpay_payment_id = payment_data.get("id")
            if not razorpay_order_id or not user_id or not razorpay_payment_id:
                return JsonResponse({"error": "Invalid webhook payload."}, status=400)
            with transaction.atomic():
                payment = Payment.objects.select_for_update().filter(razorpay_order_id=razorpay_order_id).first()
                if not payment:
                    return JsonResponse({"error": "Payment record not found."}, status=404)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.is_paid = True
                payment.save()
                if not hasattr(payment, "booking"):
                    raise Exception("Booking not found for this payment.")
                payment.booking.status = BookingStatusChoices.confirmed
                payment.booking.save()
                user = User.objects.select_for_update().filter(id=user_id).first()
                if not user:
                    return JsonResponse({"error": "User not found."}, status=404)
                bed = allocate_bed(payment.booking, user)
                if user.role != RoleTypeChoices.customer:
                    user.role = RoleTypeChoices.customer
                    user.save()
            return JsonResponse(
                {"status": "success", "message": f"Bed {bed.bed_number} allotted successfully."}, status=200
            )
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error": "Invalid Razorpay signature."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)
        except Exception:
            return JsonResponse({"error": "Internal server error."}, status=400)
