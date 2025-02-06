from django.db import models

from apps.access.models.user import User
from apps.common.model_fields import AppPhoneNumberField
from apps.common.models.base import (
    COMMON_CHAR_FIELD_MAX_LENGTH,
    COMMON_NULLABLE_FIELD_CONFIG,
    BaseModel,
    IdentityBaseModel,
)
from apps.properties.choices import GenderChoices, RoomTypesChoices


class Property(IdentityBaseModel):
    """
    Property model for the application...

    ********************************  Model Fields ********************************
    pk                  - id
    uuid                - uuid
    charField           - property_name, property_city, property_area,
                          property_location, property_janitor, property_address, property_gender
    DateTimeField       - created_at, modified_at
    EmailField          -
    PhoneNumberField    - property_phonenumber
    DecimalField        - property_latitude, property_longitude,
    """

    city = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    area = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    location = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    latitude = models.DecimalField(max_digits=19, decimal_places=16, unique=True)
    longitude = models.DecimalField(max_digits=19, decimal_places=16, unique=True)
    janitor = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    address = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    phone_number = AppPhoneNumberField(unique=True)
    gender = models.CharField(choices=GenderChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH)
    email = models.EmailField(unique=True)

    class Meta(BaseModel.Meta):
        default_related_name = "related_properties"


class Amenity(IdentityBaseModel):
    """
    Amenity model for the application...

    ********************************  Model Fields ********************************
    pk                  - id
    uuid                - uuid
    charField           - amenity_name
    DateTimeField       - created_at, modified_at
    """

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)

    class Meta(BaseModel.Meta):
        default_related_name = "related_amenities"


class PropertyAmenity(BaseModel):
    """
    PropertyAmenity model for the application...

    ********************************  Model Fields ********************************
    pk                  - id
    uuid                - uuid
    ForeignKey          - property, amenity
    DateTimeField       - created_at, modified_at
    """

    property = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    amenity = models.ForeignKey(to=Amenity, on_delete=models.CASCADE)

    class Meta(BaseModel.Meta):
        default_related_name = "related_property_amenities"
        constraints = [models.UniqueConstraint(fields=["property", "amenity"], name="unique_property_amenities")]


class RoomType(IdentityBaseModel):
    """
    RoomTypes model for the application...

    ********************************  Model Fields ********************************
    pk                  - id
    uuid                - uuid
    charField           - room_type_name
    DateTimeField       - created_at, modified_at
    """

    name = models.CharField(choices=RoomTypesChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    capacity = models.PositiveIntegerField(**COMMON_NULLABLE_FIELD_CONFIG)

    class Meta(BaseModel.Meta):
        default_related_name = "related_room_types"


class PropertyRoomType(BaseModel):
    """
    RoomTypes model for the application...

    ********************************  Model Fields ********************************
    pk                   - id
    uuid                 - uuid
    charField            - room_type_name
    DateTimeField        - created_at, modified_at
    Fk                   - room_type, property
    PositiveIntegerField - capacity, number_of_rooms
    DecimalField         - price_per_month
    BooleanField         - is_available
    """

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    room_type = models.ForeignKey(to=RoomType, on_delete=models.CASCADE)
    number_of_rooms = models.PositiveIntegerField()
    price_per_month = models.DecimalField(max_digits=19, decimal_places=2)
    total_capacity = models.PositiveIntegerField(**COMMON_NULLABLE_FIELD_CONFIG)
    is_bed_available = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        default_related_name = "related_property_room_types"
        constraints = [models.UniqueConstraint(fields=["property", "room_type"], name="unique_property_room_type")]


class Bed(BaseModel):
    """
    Bed model representing individual beds in a room.

    ********************************  Model Fields ********************************
    pk                   - id
    uuid                 - uuid
    Fk                   - property_room_type
    CharField            - bed_type
    BooleanField         - is_available
    PositiveIntegerField - bed_number
    DateTimeField        - created_at, modified_at
    """

    property_room_type = models.ForeignKey(
        PropertyRoomType, on_delete=models.CASCADE, related_name="beds", **COMMON_NULLABLE_FIELD_CONFIG
    )
    room_type = models.ForeignKey(to=RoomType, on_delete=models.CASCADE, **COMMON_NULLABLE_FIELD_CONFIG)
    user = models.ForeignKey(User, on_delete=models.CASCADE, **COMMON_NULLABLE_FIELD_CONFIG)
    is_available = models.BooleanField(default=True)
    bed_number = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_NULLABLE_FIELD_CONFIG)

    class Meta(BaseModel.Meta):
        default_related_name = "related_beds"
        constraints = [models.UniqueConstraint(fields=["property_room_type", "bed_number"], name="unique_bed_in_room")]


class TimeSlot(BaseModel):
    """
    Model for time slots

    ********************************  Model Fields ********************************
    pk                   - id
    uuid                 - uuid
    DateTimeField        - start_time, end_time
    DateTimeField        - created_at, modified_at
    """

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta(BaseModel.Meta):
        default_related_name = "related_timeslots"


class PropertyScheduleVisit(BaseModel):
    """
    Model for schedule visits

    ********************************  Model Fields ********************************
    pk                   - id
    uuid                 - uuid
    Fk                   - property, user, time_slot
    DateTimeField        - date
    DateTimeField        - created_at, modified_at
    """

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    date = models.DateTimeField()
    is_cancelled = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        default_related_name = "related_schedule_visits"
