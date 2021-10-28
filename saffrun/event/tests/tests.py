from datetime import datetime, timedelta

from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from authentication.factory import UserFactory

from event.models import Event

from .EventFactory import EventFactory


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
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access)

    def test_create_event(self):
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

    def test_update_event(self):
        event = EventFactory(owner=self.user)
        users = UserFactory.create_batch(3)
        response_event = self.client.patch(
            reverse("event", args=[event.id]),
            data={
                "title": "updated_title",
                "participants": list(map(lambda user: user.id, users)),
            },
        )
        event.refresh_from_db()
        self.assertEqual(response_event.status_code, status.HTTP_200_OK)
        self.assertEqual(event.title, "updated_title")

    def test_get_all_event(self):
        events = EventFactory.create_batch(15)
        response = self.client.get(
            reverse("get-all-events"), data={"search_query": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["events"]), len(events))

    def test_add_participants_to_event(self):
        event = EventFactory()
        users = UserFactory.create_batch(4)
        response = self.client.post(
            reverse("add-participants"),
            data={
                "event_id": event.id,
                "participants_id": list(map(lambda user: user.id, users)),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["participants"]), len(users))
