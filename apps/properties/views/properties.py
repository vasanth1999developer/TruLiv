from apps.common.helpers import haversine
from apps.common.permission_class import RoleBasedPermission
from apps.common.task import send_sms
from apps.common.views.api.base import AppAPIView, NonAuthenticatedAPIMixin
from apps.common.views.api.generic import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppModelRetrieveAPIViewSet
from apps.properties.choices import RoleTypeChoices
from apps.properties.models.properties import (
    Amenity,
    Property,
    PropertyAmenity,
    PropertyRoomType,
    PropertyScheduleVisit,
    RoomType,
    TimeSlot,
)
from apps.properties.serializers.properties import (
    AmenityListSerializer,
    AmenitySerializer,
    PropertyAmenitySerializer,
    PropertyLATandLONSerializer,
    PropertyListSerializer,
    PropertyRetriveSerializer,
    PropertyRoomListSerializer,
    PropertyRoomRetriveSerializer,
    PropertyRoomTypeSerializer,
    PropertySerializer,
    RoomTypeListSerializer,
    RoomTypeSerializer,
    ScheduleVistListSerilizer,
    ScheduleVistSerilizer,
    TimeSlotListSerializer,
    TimeSlotSerializer,
)


class PropertiesListViewSet(AppModelListAPIViewSet):
    """Property list view Set for this Application"""

    serializer_class = PropertyListSerializer
    queryset = Property.objects.all()
    search_fields = ["name", "location", "city", "area"]
    filterset_fields = [
        "location",
        "related_property_room_types__room_type__name",
        "related_property_room_types__price_per_month",
    ]
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin, RoleTypeChoices.guest]


class PropertyRetriveViewSet(AppModelRetrieveAPIViewSet):
    """Property retrieve view Set for this Application"""

    serializer_class = PropertyRetriveSerializer
    queryset = Property.objects.all()
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin, RoleTypeChoices.guest]


class AmenityCUDViewSet(AppModelCUDAPIViewSet):
    """Amenity CUD view Set for this Application"""

    serializer_class = AmenitySerializer
    queryset = Amenity.objects.all()
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class AmenityListViewSet(AppModelListAPIViewSet):
    """Amenity list view Set for this Application"""

    serializer_class = AmenityListSerializer
    queryset = Amenity.objects.all()
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class RoomTypesCUDViewSet(AppModelCUDAPIViewSet):
    """Room type CUD view Set for this Application"""

    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class RoomTypeListViewSet(AppModelListAPIViewSet):
    """Room type list view Set for this Application"""

    queryset = RoomType.objects.all()
    serializer_class = RoomTypeListSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class PropertyCUDViewSet(AppModelCUDAPIViewSet):
    """Property CUD view Set for this Application"""

    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class PropertyAmenityViewSet(AppModelCUDAPIViewSet):
    """Property amenity CUD view Set for this Application"""

    queryset = PropertyAmenity.objects.all()
    serializer_class = PropertyAmenitySerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class PropertyRoomRegistrationViewSet(AppModelCUDAPIViewSet):
    """Property room registration CUD view Set for this Application"""

    queryset = PropertyRoomType.objects.all()
    serializer_class = PropertyRoomTypeSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class PropertyRoomListViewSet(AppModelListAPIViewSet):
    """Property room registration CUD view Set for this Application"""

    queryset = PropertyRoomType.objects.all()
    serializer_class = PropertyRoomListSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class PropertyRoomRetriveViewSet(AppModelRetrieveAPIViewSet):
    """Property room registration CUD view Set for this Application"""

    queryset = PropertyRoomType.objects.all()
    serializer_class = PropertyRoomRetriveSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class NearbyPropertiesView(AppAPIView):
    """Nearby properties view Set for this Application"""

    serializer_class = PropertyLATandLONSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.guest, RoleTypeChoices.admin]

    def get(self, request, *args, **kwargs):
        """Override this method to get the nearby properties of current location"""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]
        radius = float(request.query_params.get("radius", 50))
        properties = Property.objects.all()
        nearby_places = [
            {
                "id": place.id,
                "name": place.name,
                "location": place.location,
                "distance_km": round(haversine(latitude, longitude, float(place.latitude), float(place.longitude)), 2),
            }
            for place in properties
            if haversine(latitude, longitude, float(place.latitude), float(place.longitude)) <= radius
        ]
        filtered_places = [place for place in nearby_places if place["distance_km"] > 0.0]
        sorted_places = sorted(filtered_places, key=lambda x: x["distance_km"])
        return self.send_response(sorted_places)


class TimeSlotCUDViewSet(NonAuthenticatedAPIMixin, AppModelCUDAPIViewSet):
    """Create a list of time slots"""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class TimeSlotListViewSet(NonAuthenticatedAPIMixin, AppModelListAPIViewSet):
    """Get a list of time slots"""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotListSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.admin]


class PropertyScheduleVistViewSet(AppModelCUDAPIViewSet):
    """CUD of the PropertyScheduleVistViewSet for the user"""

    queryset = PropertyScheduleVisit.objects.all()
    serializer_class = ScheduleVistSerilizer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.guest]

    def create(self, request, *args, **kwargs):
        """Ovverride this method to set user for a schedule visit."""

        user = self.get_request().user
        request_data = {
            "user": self.get_user().id,
            "property": self.get_request().data.get("property"),
            "time_slot": self.get_request().data.get("time_slot"),
            "date": self.get_request().data.get("date"),
        }
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        property_id = request_data["property"]
        property_obj = Property.objects.get(id=property_id)
        property_phone_number = property_obj.phone_number
        user_message = f"Your visit is scheduled on {request_data['date']} at {request_data['time_slot']}."
        janitor_message = f"A property visit is scheduled on {request_data['date']} at {request_data['time_slot']}."
        send_sms.delay(str(user.phone_number), user_message)
        send_sms.delay(str(property_phone_number), janitor_message)
        return self.send_response(data={"You Visit to the Property Scheduled..."})

    def update(self, request, *args, **kwargs):
        """Override this method to ensure user and validate date when updating a schedule visit."""

        instance = self.get_object()
        request_data = {
            "user": self.get_user().id,
            "property": self.get_request().data.get("property", instance.property.id),
            "time_slot": self.get_request().data.get("time_slot", instance.time_slot.id),
            "date": self.get_request().data.get("date", instance.date),
        }
        serializer = self.get_serializer(instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.send_response(data={"message": "Your scheduled visit has been updated."})


class ScheduleVistListOfUserViewSet(AppModelListAPIViewSet):
    """ "List of properties ScheduleVistListOfUserViewSet of the User"""

    serializer_class = ScheduleVistListSerilizer
    permission_classes = [RoleBasedPermission]
    allowed_roles = [RoleTypeChoices.guest]

    def get_queryset(self):
        """Override get_queryset()"""

        return PropertyScheduleVisit.objects.filter(user=self.get_user())
