from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import serializers, status
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.response import Response

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ManyCategorySerializer(serializers.Serializer):
    categories = CategorySerializer(many=True)


class AllCategorySerializer(serializers.Serializer):
    search_query = serializers.CharField(
        max_length=200, allow_null=False, allow_blank=True
    )
