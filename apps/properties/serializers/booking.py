from rest_framework import serializers

from apps.properties.models.booking import Booking


class BookingSerializer(serializers.ModelSerializer):
    """Booking serializer class"""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)

    class Meta:
        model = Booking
        fields = ["property", "room_type", "joining_date", "amount"]
