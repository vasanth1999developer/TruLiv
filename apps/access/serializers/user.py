from rest_framework import serializers

from apps.access.models.user import User
from apps.common.serializers import AppWriteOnlyModelSerializer


class UserSerializer(AppWriteOnlyModelSerializer):
    """Serializer for user model."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = ["id", "phone_number", "first_name", "last_name", "gender", "email"]


class PhoneNumberSerializer(serializers.Serializer):
    """Validator for phone_number"""

    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        """Ensure phone number contains exactly 10 digits."""

        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
