from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from .utils import random_string_generator
from .models import Invoice
from profile.models import UserProfile


class PayInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('amount', 'owner', 'filters')

    def create(self, validated_data):
        debtor_id = get_object_or_404(UserProfile, user=self.context['request'].user.id)
        return Invoice.objects.create(debtor=debtor_id, **self.validated_data, token='S' + random_string_generator(11), reference_code=random_string_generator(24))

