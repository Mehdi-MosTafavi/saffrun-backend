from datetime import datetime, timedelta

from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from authentication.factory import UserFactory

from event.models import Event


class EventTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.set_password("123")
        self.user.save()
        response = self.client.post(
            reverse("auth:login"),
            data={"username": self.user.username, "password": "123"},
        )
        self.access = response.data["access"]

    def test_create_event(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access)
        response_event = self.client.post(
            reverse("add-event"),
            data={
                "title": "test_title",
                "owner": self.user.id,
                "discount": 15,
                "start_datetime": datetime.now(),
                "end_datetime": datetime.now() + timedelta(days=1),
            },
        )
        event = Event.objects.get(owner=self.user.id)
        self.assertEqual(response_event.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_event.data["id"], event.id)
