from profile.models import UserProfile
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Invoice
from .utils import random_string_generator


class PayInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('amount', 'owner', 'filters')

    def create(self, validated_data):
        debtor_id = get_object_or_404(UserProfile, user=self.context['request'].user.id)
        return Invoice.objects.create(debtor=debtor_id, **self.validated_data, token='S' + random_string_generator(11),
                                      reference_code=random_string_generator(24))


class ListInvoice(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('id', 'amount', 'owner', 'debtor')


class ManyPaymentSerializer(serializers.Serializer):
    pages = serializers.IntegerField()
    payments = serializers.ListField(min_length=0, child=serializers.DictField())
