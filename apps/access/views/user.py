from apps.access.models.user import User
from apps.access.serializers.user import UserSerializer
from apps.common.views.api.base import NonAuthenticatedAPIMixin
from apps.common.views.api.generic import AppModelCreatePIViewSet


class UserCreateAPIView(NonAuthenticatedAPIMixin, AppModelCreatePIViewSet):
    """Create the user ApiView for user registration"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
