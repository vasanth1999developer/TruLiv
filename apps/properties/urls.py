from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.properties.views.booking import CreateRazorpayOrderView
from apps.properties.views.properties import (
    AmenityCUDViewSet,
    AmenityListViewSet,
    NearbyPropertiesView,
    PropertiesListViewSet,
    PropertyAmenityViewSet,
    PropertyCUDViewSet,
    PropertyRetriveViewSet,
    PropertyRoomListViewSet,
    PropertyRoomRegistrationViewSet,
    PropertyRoomRetriveViewSet,
    PropertyScheduleVistViewSet,
    RoomTypeListViewSet,
    RoomTypesCUDViewSet,
    ScheduleVistListOfUserViewSet,
    TimeSlotCUDViewSet,
    TimeSlotListViewSet,
)
from apps.properties.views.webhook import RazorpayWebhookView

API_URL_PREFIX = "v1/"

router = AppSimpleRouter()

# Amenities API
router.register(f"{API_URL_PREFIX}amenities", AmenityCUDViewSet, basename="amenity")
router.register(f"{API_URL_PREFIX}amenities-list", AmenityListViewSet, basename="amenity-list")

# Set_Property_Amenities API
router.register(f"{API_URL_PREFIX}set-property-Amenities", PropertyAmenityViewSet, basename="set-property-Amenities")

# RoomType API
router.register(f"{API_URL_PREFIX}roomTypes", RoomTypesCUDViewSet, basename="room")
router.register(f"{API_URL_PREFIX}roomType-list", RoomTypeListViewSet, basename="room-type-list")

# Property Api
router.register(f"{API_URL_PREFIX}property", PropertyCUDViewSet, basename="property")
router.register(f"{API_URL_PREFIX}properties", PropertiesListViewSet, basename="properties")
router.register(f"{API_URL_PREFIX}get-propertie", PropertyRetriveViewSet, basename="get-propertie")

# Property Room Registration API
router.register(
    f"{API_URL_PREFIX}property-room-registration",
    PropertyRoomRegistrationViewSet,
    basename="property-room-registration",
)
router.register(f"{API_URL_PREFIX}property-room-List", PropertyRoomListViewSet, basename="property-room-list")
router.register(f"{API_URL_PREFIX}get-property-room", PropertyRoomRetriveViewSet, basename="get-property-room")

# Razorpay PreBooking API
router.register(f"{API_URL_PREFIX}booking", CreateRazorpayOrderView, basename="create-razorpay-order")

# Time Slot Management API
router.register(f"{API_URL_PREFIX}time-slot", TimeSlotCUDViewSet, basename="Create-time-slot")
router.register(f"{API_URL_PREFIX}time-slot-list", TimeSlotListViewSet, basename="time-slot-list")

# Property Schedule Visit API
router.register(f"{API_URL_PREFIX}schedule-visit", PropertyScheduleVistViewSet, basename="schedule-visit")
router.register(
    f"{API_URL_PREFIX}schedule-visit-list", ScheduleVistListOfUserViewSet, basename="schedule-visit-of-user"
)

urlpatterns = [
    path(f"{API_URL_PREFIX}nearby-places", NearbyPropertiesView.as_view(), name="nearby-places"),
    path("razorpay/webhook/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
] + router.urls
