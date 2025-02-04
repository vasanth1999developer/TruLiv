from django.urls import path

from apps.access.views.login import LoginOTPView, LogoutUserAPIView, ValidateOTPView
from apps.access.views.user import UserCreateAPIView
from apps.common.routers import AppSimpleRouter

V1_API_URL_PREFIX = "api/v1/access"

router = AppSimpleRouter()

# User API
router.register(f"{V1_API_URL_PREFIX}/user-registration", UserCreateAPIView, basename="amenity-list")

urlpatterns = [
    # ----------------------------- Authentication API's --------------------------------
    path(f"{V1_API_URL_PREFIX}/login/", LoginOTPView.as_view()),
    path(f"{V1_API_URL_PREFIX}/otp-validation/", ValidateOTPView.as_view()),
    path(f"{V1_API_URL_PREFIX}/logout/", LogoutUserAPIView.as_view()),
] + router.urls
