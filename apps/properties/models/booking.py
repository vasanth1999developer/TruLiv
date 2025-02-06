from django.db import models

from apps.access.models.user import User
from apps.common.models.base import COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, COMMON_CHAR_FIELD_MAX_LENGTH, BaseModel
from apps.properties.choices import BookingStatusChoices, StatusChoices
from apps.properties.models.properties import Bed, Property, PropertyRoomType, RoomType


class Booking(BaseModel):
    """
    Booking model for the application...

    ********************************  Model Fields ********************************
    pk                  - id
    uuid                - uuid
    Fk                  - user, property, room_type, bed
    DateField           - joining_date
    CharField           - status (choices: pending, confirmed, cancelled)
    DateTimeField       - created_at, modified_at
    """

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    property = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    room_type = models.ForeignKey(to=RoomType, on_delete=models.CASCADE)
    joining_date = models.DateField()
    status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=BookingStatusChoices.choices,
        default=BookingStatusChoices.pending,
    )
    bed = models.ForeignKey(to=Bed, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, on_delete=models.SET_NULL)
    is_paid_advance = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        default_related_name = "related_bookings"


class Payment(BaseModel):
    """
    Payment model for the application...

    ********************************  Model Fields ********************************
    pk                      - id
    Fk                      - booking (OneToOne)
    CharField               - razorpay_order_id (unique), razorpay_payment_id, razorpay_signature
    DecimalField            - amount
    BooleanField            - is_paid (default: False)
    DateTimeField           - created_at, modified_at
    """

    booking = models.OneToOneField(to=Booking, on_delete=models.CASCADE, related_name="payment")
    razorpay_order_id = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    razorpay_payment_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    razorpay_signature = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    razorpay_payment_link_order_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        default_related_name = "related_payments"


class RentalPayment(BaseModel):
    """
    Payment model for the application...

    ********************************  Model Fields ********************************
    pk                      - id
    Fk                      - booking (OneToOne)
    CharField               - razorpay_order_id (unique), razorpay_payment_id, razorpay_signature
    DecimalField            - amount
    BooleanField            - is_paid (default: False)
    DateTimeField           - created_at, modified_at
    """

    booking = models.ForeignKey(to=Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    property = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    room_type = models.ForeignKey(to=PropertyRoomType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    daily_rent = models.DecimalField(max_digits=10, decimal_places=2)
    days_charged = models.IntegerField()
    due_date = models.DateField()
    status = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=StatusChoices.choices, default=StatusChoices.pending
    )
    payment_link = models.URLField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    transaction_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    class Meta(BaseModel.Meta):
        default_related_name = "related_rental_payments"
