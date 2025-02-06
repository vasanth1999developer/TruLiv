from django.conf import settings
from twilio.rest import Client


class WhatsappClient:
    """Whatsapp REST API Client for Twilio."""

    def __init__(self):
        """Initialize the Twilio client."""

        self.account_sid = settings.TWILIO_CONFIG["account_sid"]
        self.auth_token = settings.TWILIO_CONFIG["auth_token"]
        self.whatsapp_number = settings.TWILIO_CONFIG["whatsapp_number"]
        self.client = Client(self.account_sid, self.auth_token)

    def get_headers(self):
        """Headers necessary for authorization (not needed for Twilio as it uses authentication via SID and token)."""
        return {}

    def process_payload(self, template_name, body_values, **kwargs):
        """Process the payload for Twilio's WhatsApp API."""

        if person := kwargs.get("person"):
            name = person.name
            recipient_phone = str(person.phone_number).replace("+", "")
        else:
            name = ""
            phone_number = kwargs.get("phone")
            recipient_phone = f"whatsapp: +91{phone_number}"

        message_body = f"Hello {name}, your OTP is: {body_values.get('number')}. It is valid for 60 seconds."

        return {"from_": f"whatsapp: {self.whatsapp_number}", "body": message_body, "to": recipient_phone}

    def post(self, data, params={}):
        """Send WhatsApp message via Twilio API."""

        try:
            message = self.client.messages.create(from_=data["from_"], body=data["body"], to=data["to"])
            return True, message
        except Exception as e:
            return False, str(e)
