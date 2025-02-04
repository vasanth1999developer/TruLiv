

from apps.access.models.user import User
from apps.common.serializers import AppWriteOnlyModelSerializer


class UserSerializer(AppWriteOnlyModelSerializer):
    """Serializer for user model."""
    
    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = ["id","phone_number", "first_name", "last_name", "gender", "email"]
