from celery import shared_task
from django.conf import settings
from twilio.rest import Client


@shared_task
def send_sms(phone_number, message):
    """
    Sends an SMS using Twilio API asynchronously.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    client.messages.create(body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number)
