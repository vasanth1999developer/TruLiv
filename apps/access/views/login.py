from rest_framework.authtoken.models import Token

from apps.access.models.user import User
from apps.common.helpers import generate_otp, validate_otp
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.common.whatsapp_service import WhatsappClient


class LoginOTPView(NonAuthenticatedAPIMixin, AppAPIView):
    """Used to trigger OTP for any user in the application if they exist."""

    def post(self, request):
        phone_number = self.get_request().data.get("phone_number")
        if phone_number:
            otp = generate_otp(phone_number, expiry=60)
            client = WhatsappClient()
            payload = client.process_payload(
                template_name="identity_confirm_template",
                body_values={"number": otp},
                phone=phone_number,
            )
            success, response = client.post(data=payload)
            if success and response.status in ["queued", "sent", "delivered"]:
                return self.send_response("Otp sent to the registered mobile number.")
            else:
                error_message = response if isinstance(response, str) else response.error_message
                return self.send_error_response(f"Failed to send OTP: {error_message}")
        return self.send_error_response("Please enter your phone number")


class ValidateOTPView(NonAuthenticatedAPIMixin, AppAPIView):
    """Validate provided OTP and phone_number and return authorization token."""

    def post(self, request):
        """Handle on POST"""

        phone_number = self.get_request().data.get("phone_number")
        otp = self.get_request().data.get("otp")
        if not phone_number or not otp:
            return self.send_error_response()
        if validate_otp(phone_number, otp):
            try:
                user = User.objects.get(phone_number=f"+91{phone_number}")
                if user:
                    token, _ = Token.objects.get_or_create(user=user)
                    return self.send_response(data={"token": token.key})
                else:
                    return self.send_response()
            except Exception:
                return self.send_response("OTP Verified Successfully.")
        return self.send_error_response("Invalid OTP")


class LogoutUserAPIView(AppAPIView):
    """Invalidate a token of current session and logout user."""

    def post(self, *args, **kwargs):
        """Handle on post."""

        user = self.get_authenticated_user()
        try:
            user.auth_token.delete()
            return self.send_response()
        except Exception:
            return self.send_error_response()
