from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.properties.views.properties import ScheduleVistListOfUserViewSet

User = get_user_model()


class TestScheduleVistListOfUserViewSet(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.view = ScheduleVistListOfUserViewSet.as_view({"get": "list"})
