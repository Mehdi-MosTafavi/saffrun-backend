from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView , ListAPIView
from rest_framework.response import Response

from .models import Category
from .serializers import CategorySerializer, AllCategorySerializer, ManyCategorySerializer


# Create your views here.
from core.responses import ErrorResponse

# @swagger_auto_schema(
#     method="get",
#     responses={200: ManyCategorySerializer, 406: ErrorResponse.INVALID_DATA},
# )
class CategoryGetAll(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



# @api_view(["GET"])
# def get_all_categories(request):
#     """
#     Getting all the categories
#     """
#     categories = Category.objects.all()
#     return Response(
#         {"categories": CategorySerializer(instance=categories, many=True).data},
#         status=status.HTTP_200_OK,
#     )
