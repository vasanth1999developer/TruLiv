import string
from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from apps.common.serializers import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.properties.choices import RoomTypesChoices
from apps.properties.models.properties import (
    Amenity,
    Bed,
    Property,
    PropertyAmenity,
    PropertyRoomType,
    PropertyScheduleVisit,
    RoomType,
    TimeSlot,
)


class PropertySerializer(AppWriteOnlyModelSerializer):
    """Serializer for property model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Property
        fields = [
            "name",
            "location",
            "area",
            "city",
            "latitude",
            "longitude",
            "janitor",
            "address",
            "phone_number",
            "gender",
            "email",
        ]


class AmenitySerializer(AppWriteOnlyModelSerializer):
    """Serializer for amenity model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Amenity
        fields = ["name"]


class AmenityListSerializer(AppReadOnlyModelSerializer):
    """Serializer for amenity list model."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Amenity
        fields = ["name"]


class PropertyAmenityListSerializer(AppReadOnlyModelSerializer):
    """Serializer for Property Amenity list model."""

    amenity = AmenityListSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = PropertyAmenity
        fields = ["amenity"]


class PropertyRetriveSerializer(AppReadOnlyModelSerializer):
    """Ssrilalizer to retrieve the properties"""

    related_property_amenities = PropertyAmenityListSerializer(many=True, read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Property
        fields = [
            "name",
            "location",
            "area",
            "city",
            "latitude",
            "longitude",
            "janitor",
            "address",
            "phone_number",
            "gender",
            "email",
            "related_property_amenities",
        ]


class PropertyAmenitySerializer(AppWriteOnlyModelSerializer):
    """Serializer for Property Amenity model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PropertyAmenity
        fields = ["property", "amenity"]


class RoomTypeSerializer(AppWriteOnlyModelSerializer):
    """Serializer for rome type model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = RoomType
        fields = ["name"]
        read_only_fields = ["capacity"]

    def create(self, validated_data):
        """Create method is overridden to set the capacity of the roomtype Automatically"""

        instance = super().create(validated_data=validated_data)
        match instance.name:
            case RoomTypesChoices.single_occupancy:
                instance.capacity = 1
            case RoomTypesChoices.double_occupancy:
                instance.capacity = 2
            case RoomTypesChoices.triple_occupancy:
                instance.capacity = 3
            case RoomTypesChoices.quadruple_occupancy:
                instance.capacity = 4
            case RoomTypesChoices.quintuple_occupancy:
                instance.capacity = 5
            case RoomTypesChoices.sixtuple_occupancy:
                instance.capacity = 6
        instance.save()
        return instance


class RoomTypeListSerializer(AppReadOnlyModelSerializer):
    """Serializer for room type list model."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = RoomType
        fields = ["id", "name"]


class PropertyRoomTypeSerializer(AppWriteOnlyModelSerializer):
    """Serializer for room type list model"""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PropertyRoomType
        fields = ["property", "room_type", "number_of_rooms", "price_per_month", "total_capacity"]
        read_only_fields = ["is_Available", "total_capacity"]

    def create(self, validated_data):
        """Override to calculate the capacity and auto-create bed details."""

        instance = super().create(validated_data=validated_data)
        self._update_beds(instance)
        return instance

    def update(self, instance, validated_data):
        """Override to handle bed updates when the number of rooms changes."""

        with transaction.atomic():
            instance = super().update(instance, validated_data)
            self._update_beds(instance)
        return instance

    def _update_beds(self, instance):
        """
        Helper method to calculate capacity and update bed details.
        Adds or removes beds based on the current number of rooms.
        """

        room_type = instance.room_type
        room_type_id = instance.room_type.id
        room_type = RoomType.objects.get(id=room_type_id)
        instance.total_capacity = instance.number_of_rooms * room_type.capacity
        existing_beds = Bed.objects.filter(property_room_type=instance)
        current_bed_count = existing_beds.count()
        required_bed_count = room_type.capacity * instance.number_of_rooms
        if required_bed_count < current_bed_count:
            beds_to_remove = current_bed_count - required_bed_count
            beds_to_delete = existing_beds.order_by("-id")[:beds_to_remove]
            for bed in beds_to_delete:
                bed.delete()
        elif required_bed_count > current_bed_count:
            suffix_map = {
                RoomTypesChoices.single_occupancy: string.ascii_uppercase,
                RoomTypesChoices.double_occupancy: [f"A{chr(i)}" for i in range(65, 65 + room_type.capacity)],
                RoomTypesChoices.triple_occupancy: [f"B{chr(i)}" for i in range(65, 65 + room_type.capacity)],
                RoomTypesChoices.quadruple_occupancy: [f"C{chr(i)}" for i in range(65, 65 + room_type.capacity)],
                RoomTypesChoices.quintuple_occupancy: [f"D{chr(i)}" for i in range(65, 65 + room_type.capacity)],
                RoomTypesChoices.sixtuple_occupancy: [f"E{chr(i)}" for i in range(65, 65 + room_type.capacity)],
            }
            suffix_list = suffix_map.get(room_type.name.lower(), string.ascii_uppercase)
            current_room_count = current_bed_count // room_type.capacity
            for room_no in range(current_room_count + 1, instance.number_of_rooms + 1):
                for bed_no in range(1, room_type.capacity + 1):
                    bed_suffix = suffix_list[bed_no - 1]
                    bed_number = f"R{room_no: 03d}-{bed_suffix}"
                    room_type = RoomType.objects.get(id=room_type_id)
                    Bed.objects.create(property_room_type=instance, room_type=room_type, bed_number=bed_number)
        instance.save()
        return instance


class PropertyLATandLONSerializer(serializers.Serializer):
    """Serializer for properties latitude and longitude"""

    latitude = serializers.DecimalField(max_digits=22, decimal_places=20)
    longitude = serializers.DecimalField(max_digits=22, decimal_places=20)

    def validate_latitude(self, value):
        """Validate that latitude is between -90 and 90 and has no more than 2 digits before the decimal point."""

        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        if len(str(int(value))) > 2:
            raise serializers.ValidationError("Latitude cannot have more than 2 digits before the decimal point.")
        return value

    def validate_longitude(self, value):
        """Validate that longitude is between -180 and 180 and has no more than 3 digits before the decimal point."""

        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        if len(str(int(value))) > 3:
            raise serializers.ValidationError("Longitude cannot have more than 3 digits before the decimal point.")
        return value

    def validate(self, data):
        """Additional validation for both latitude and longitude."""

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude == 0 and longitude == 0:
            raise serializers.ValidationError("Latitude and longitude cannot both be 0.")
        return data


class PropertyHelperSerializer(AppReadOnlyModelSerializer):
    """Serializer for property model."""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Property
        fields = [
            "id",
            "name",
            "location",
            "city",
            "janitor",
            "address",
            "phone_number",
        ]


class RoomTypeHelperSerializer(AppReadOnlyModelSerializer):
    """Serilaizer for RoomType object"""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = RoomType
        fields = ["id", "name", "capacity"]


class PropertyRoomListSerializer(AppReadOnlyModelSerializer):
    """Serializer for room type list model."""

    property = PropertyHelperSerializer(read_only=True)
    room_type = RoomTypeHelperSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = PropertyRoomType
        fields = [
            "id",
            "property",
            "room_type",
            "number_of_rooms",
            "price_per_month",
            "total_capacity",
            "is_bed_available",
        ]


class PropertyRoomRetriveSerializer(AppReadOnlyModelSerializer):
    """Serializer for room type for retrive"""

    property = PropertyHelperSerializer(read_only=True)
    room_type = RoomTypeHelperSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = PropertyRoomType
        fields = [
            "id",
            "property",
            "room_type",
            "number_of_rooms",
            "price_per_month",
            "total_capacity",
            "is_bed_available",
        ]


class TimeSlotSerializer(AppWriteOnlyModelSerializer):
    """Serilizer for time slots"""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = TimeSlot
        fields = ["id", "start_time", "end_time"]

    def to_internal_value(self, data):
        """Converts 12-hour format (AM/PM) to 24-hour format before saving to DB."""

        data["start_time"] = datetime.strptime(data["start_time"], "%I:%M %p").time()
        data["end_time"] = datetime.strptime(data["end_time"], "%I:%M %p").time()
        return super().to_internal_value(data)


class TimeSlotListSerializer(AppReadOnlyModelSerializer):
    """Serializer for time slots list model."""

    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = TimeSlot
        fields = ["id", "start_time", "end_time"]

    def get_start_time(self, obj):
        """Converts from 24-hour format (database) to 12-hour AM/PM format"""

        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        """Converts from 24-hour format (database) to 12-hour AM/PM format"""

        return obj.end_time.strftime("%I:%M %p")


class ScheduleVistSerilizer(AppWriteOnlyModelSerializer):
    """Serializer for schedule visits"""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = PropertyScheduleVisit
        fields = ["id", "property", "user", "time_slot", "date"]

    def validate_date(self, value):
        """Ensure the date is not in the past"""

        today = datetime.today().date()
        if value.date() < today:
            raise serializers.ValidationError("The visit date cannot be in the past.")
        return value


class PropertyScheduleVistSerilizer(AppReadOnlyModelSerializer):
    """Serializer for PropertyScheduleVistSerilizer"""

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Property
        fields = [
            "name",
            "latitude",
            "longitude",
            "janitor",
            "address",
            "phone_number",
        ]


class ScheduleVistListSerilizer(AppReadOnlyModelSerializer):
    """Serilizer List for ScheduleVistList"""

    property = PropertyScheduleVistSerilizer(read_only=True)
    time_slot = TimeSlotListSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = PropertyScheduleVisit
        fields = ["id", "property", "user", "time_slot", "date"]


class PropertyRoomRetriveForPropertyListSerializer(AppReadOnlyModelSerializer):
    """Serializer for room type for retrive"""

    room_type = RoomTypeHelperSerializer(read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = PropertyRoomType
        fields = ["id", "room_type", "number_of_rooms", "price_per_month", "total_capacity", "is_bed_available"]


class PropertyListSerializer(AppReadOnlyModelSerializer):
    """Ssrilalizer to list the properties"""

    related_property_amenities = PropertyAmenityListSerializer(many=True, read_only=True)
    related_property_room_types = PropertyRoomRetriveForPropertyListSerializer(many=True, read_only=True)

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Property
        fields = [
            "id",
            "name",
            "location",
            "area",
            "city",
            "janitor",
            "address",
            "phone_number",
            "gender",
            "email",
            "related_property_amenities",
            "related_property_room_types",
        ]
