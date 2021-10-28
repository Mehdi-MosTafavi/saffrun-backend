from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from event.models import Event

from authentication.factory import UserFactory


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Faker("first_name")
    description = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
    start_datetime = timezone.now().astimezone(timezone.get_current_timezone())
    end_datetime = timezone.now().astimezone(
        timezone.get_current_timezone()
    ) + timedelta(days=1, hours=2)
    discount = factory.Faker("pyint", min_value=0, max_value=80)
