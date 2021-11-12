from django.contrib.auth.models import User
from django.db.models import Q, Count, F
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from core.responses import ErrorResponse
from datetime import timedelta, datetime
from .utils import check_collision, create_reserve_objects
from .models import Reservation
from event.serializers import SpecificEventSerializer

from authentication.serializers import ShortUserSerializer


class ReservePeriodSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    duration = serializers.IntegerField(required=False)
    period_count = serializers.IntegerField(required=False)
    capacity = serializers.IntegerField(required=True)

    def validate(self, data):
        if data.get("duration") < 5:
            raise serializers.ValidationError(ErrorResponse.DURATION_ERROR)
        if not data.get("duration") and not data.get("period_count"):
            raise serializers.ValidationError(
                ErrorResponse.DURATION_OR_COUNT_ERROR
            )
        return data

    def create(self, validated_data, **kwargs):
        start_datetime = datetime.combine(
            kwargs["date"], validated_data["start_time"]
        )
        end_datetime = datetime.combine(
            kwargs["date"], validated_data["end_time"]
        )
        if not check_collision(
            start_datetime,
            end_datetime,
            kwargs["owner"],
        ):
            total_duration = end_datetime - start_datetime
            total_duration = total_duration.seconds // 60

            return create_reserve_objects(
                validated_data,
                total_duration,
                start_datetime,
                owner=kwargs["owner"],
            )
        else:
            return ErrorResponse.COLLISION_CODE


class AllReservesOfDaySerializer(serializers.Serializer):
    reserve_periods = serializers.ListField(
        allow_empty=False, child=ReservePeriodSerializer()
    )

    def create(self, validated_data, **kwargs):
        successful_reserve_count = 0
        period_collision_count = 0
        date = kwargs["day_date"]
        while date <= kwargs["end_date"]:
            for period in validated_data["reserve_periods"]:
                period_serializer = ReservePeriodSerializer(data=period)
                if not period_serializer.is_valid():
                    return False
                response = period_serializer.create(
                    period_serializer.validated_data,
                    owner=kwargs["owner"],
                    date=date,
                )
                if response == ErrorResponse.COLLISION_CODE:
                    period_collision_count += 1
                else:
                    successful_reserve_count += response
            date += timedelta(days=7)
        return successful_reserve_count, period_collision_count


class CreateReservesSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    days_list = serializers.ListField(
        allow_empty=False, required=True, child=AllReservesOfDaySerializer()
    )

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                ErrorResponse.DATETIME_PRIORITY_ERROR
            )
        return data

    def create(self, validated_data, **kwargs):
        successful_reserve_count = 0
        period_collision_count = 0
        for index, day in enumerate(validated_data["days_list"]):
            day_serializer = AllReservesOfDaySerializer(data=day)
            if not day_serializer.is_valid():
                return False
            response = day_serializer.create(
                day_serializer.validated_data,
                owner=kwargs["owner"],
                day_date=validated_data["start_date"] + timedelta(days=index),
                end_date=validated_data["end_date"],
            )
            successful_reserve_count += response[0]
            period_collision_count += response[1]
        return successful_reserve_count, period_collision_count


class GetAllReservesSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_count = serializers.IntegerField()


class PastFutureReserveSerializer(serializers.Serializer):
    class AbstractReserveSerializer(serializers.Serializer):
        date = serializers.DateField()
        fill = serializers.IntegerField()
        available = serializers.IntegerField()

    class ReserveFutureSeriallizer(AbstractReserveSerializer):
        next_reserve = serializers.TimeField(allow_null=True)

    past = serializers.ListField(child=AbstractReserveSerializer())
    future = serializers.ListField(child=ReserveFutureSeriallizer())


class DateSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.DateField())


class DaySerializer(serializers.Serializer):
    date = serializers.DateField()


class ReserveSerializer(serializers.ModelSerializer):
    owner = ShortUserSerializer()
    start_time = serializers.SerializerMethodField(method_name="get_start_time")
    end_time = serializers.SerializerMethodField(method_name="get_end_time")

    def get_start_time(self, reservation):
        return reservation.get_start_datetime().time()

    def get_end_time(self, reservation):
        return reservation.get_end_datetime().time()

    class Meta:
        model = Reservation
        fields = ["id", "owner", "start_time", "end_time"]


class DayDetailSerializer(serializers.Serializer):
    reserves = ReserveSerializer(many=True)
    events = SpecificEventSerializer(many=True)
