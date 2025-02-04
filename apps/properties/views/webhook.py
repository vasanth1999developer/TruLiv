import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
import razorpay
from django.db.models import Q
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
            razorpay_order_id =  payment_data.get("notes", {}).get("razorpay_order_id")
            user =  payment_data.get("notes", {}).get("user_id")            
            razorpay_payment_id = payment_data.get("id")
            payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
            payment.razorpay_payment_id = razorpay_payment_id
            payment.is_paid = True
            payment.save()
            payment.booking.status = BookingStatusChoices.confirmed
            payment.booking.save()
            print("webhook-------------------------------------------------------------------------------------------------------------")
            bed = allocate_bed(payment.booking, user) 
            user = User.objects.filter(id=user).first()
            if user and user.role != RoleTypeChoices.customer:
                user.role = RoleTypeChoices.customer
                user.save()            
            return JsonResponse({
                "status": "success",
                "message": f"Bed {bed.bed_number} allotted successfully."
            }, status=200)            

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
