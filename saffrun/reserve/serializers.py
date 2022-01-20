from datetime import datetime, timedelta

from core.responses import ErrorResponse
from core.serializers import ImageAvatarSerializer
from core.serializers import ImageSerializer
from django.utils import timezone
from event.serializers import SpecificEventSerializer
from profile.serializers import EmployeeProfileSerializer
from rest_framework import serializers

from .models import Reservation
from .utils import check_collision, create_reserve_objects


class ReservePeriodSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    duration = serializers.IntegerField(required=False)
    period_count = serializers.IntegerField(required=False)
    capacity = serializers.IntegerField(required=True)

    def validate(self, data):
        if data.get("duration") and data.get("duration") < 5:
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
                price=kwargs["price"]
            )
        else:
            return ErrorResponse.COLLISION_CODE


class AllReservesOfDaySerializer(serializers.Serializer):
    reserve_periods = serializers.ListField(
        allow_empty=True, child=ReservePeriodSerializer(), allow_null=True
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
                    price=kwargs["price"],
                    date=date
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
    price = serializers.IntegerField()
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
            new_reserve_count, new_collision_count = day_serializer.create(
                day_serializer.validated_data,
                owner=kwargs["owner"],
                day_date=validated_data["start_date"] + timedelta(days=index),
                end_date=validated_data["end_date"],
                price=validated_data["price"]
            )
            successful_reserve_count += new_reserve_count
            period_collision_count += new_collision_count
        return successful_reserve_count, period_collision_count


class AbstractReserveSerializer(serializers.Serializer):
    date = serializers.DateField()
    fill = serializers.IntegerField()
    available = serializers.IntegerField()


class ReserveFutureSeriallizer(AbstractReserveSerializer):
    next_reserve = serializers.TimeField(allow_null=True)


class DateSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.DateField())


class DaySerializer(serializers.Serializer):
    date = serializers.DateField()


class ReserveSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(method_name="get_owner")
    start_time = serializers.SerializerMethodField(method_name="get_start_time")
    end_time = serializers.SerializerMethodField(method_name="get_end_time")
    image = serializers.SerializerMethodField()

    def get_owner(self, reservation):
        return {
            "id": reservation.owner.id,
            "username": reservation.owner.business.title if reservation.owner.business is not None else reservation.owner.user.get_full_name()
        }

    def get_start_time(self, reservation):
        return reservation.get_start_datetime().time()

    def get_end_time(self, reservation):
        return reservation.get_end_datetime().time()

    def get_image(self, obj):
        return ImageSerializer(instance=obj.owner.business.images.all()[0]).data

    class Meta:
        model = Reservation
        fields = ["id", "owner", "start_time", "end_time", "price", "image"]


class ReserveOwnerDetail(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField(method_name="get_start_time")
    end_time = serializers.SerializerMethodField(method_name="get_end_time")
    date = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ["id", "capacity", 'date', "start_time", "end_time", 'participants', "price"]

    def get_participants(self, obj):
        particpiants_list = []
        for participant in obj.participants.all():
            particpiants_list.append({
                'id': participant.id,
                'name': participant.user.username,
                'image': ImageAvatarSerializer(instance=participant.avatar).data
            })
        return particpiants_list

    def get_start_time(self, reservation):
        return reservation.get_start_datetime().time()

    def get_end_time(self, reservation):
        return reservation.get_end_datetime().time()

    def get_date(self, reservation):
        return reservation.get_start_datetime().date()


class DayDetailSerializer(serializers.Serializer):
    reserves = ReserveSerializer(many=True)
    events = SpecificEventSerializer(many=True)


class GetAdminSerializer(serializers.Serializer):
    admin_id = serializers.IntegerField()


class ReserveAbstractSerializer(serializers.Serializer):
    reserve_id = serializers.IntegerField()
    datetime = serializers.DateTimeField()


class NextSevenDaysSerializer(serializers.Serializer):
    nearest = ReserveAbstractSerializer(allow_null=True)
    next_seven_days = serializers.ListField(
        child=serializers.ListField(child=ReserveAbstractSerializer())
    )


class CurrentNearestReserveSerializer(serializers.Serializer):
    current_reserve = ReserveOwnerDetail()
    nearest_reserves = ReserveOwnerDetail(many=True)


class ReserveEmployeeSerializer(serializers.Serializer):
    reserve_id = serializers.IntegerField()


class ReserveHistorySerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField("get_status")
    owner = EmployeeProfileSerializer()
    image = serializers.SerializerMethodField()

    @staticmethod
    def get_status(reserve):
        if reserve.get_start_datetime() > timezone.now():
            return "NOT STARTED"
        if reserve.get_start_datetime() <= timezone.now() <= reserve.get_end_datetime():
            return "RUNNING"
        if reserve.get_end_datetime() < timezone.now():
            return "FINISHED"

    def get_image(self, obj):
        return ImageSerializer(instance=obj.owner.avatar).data

    class Meta:
        model = Reservation
        fields = ["id", "owner", "image", "start_datetime", "end_datetime", "price", "status"]


class ReserveDetailSerializer(serializers.Serializer):
    date = serializers.DateField()
    number_of_reservation = serializers.IntegerField()
    payment_of_date = serializers.IntegerField()
    number_of_users = serializers.IntegerField()
    number_of_full_reservation = serializers.IntegerField()
    number_of_half_full_reservation = serializers.IntegerField()
    number_of_empty_reservation = serializers.IntegerField()
    nearest_reserve = serializers.DictField()
    data_of_chart = serializers.ListField(child=serializers.DictField())


class ReserveRemoveSerializer(serializers.Serializer):
    reserve_id = serializers.IntegerField()


class ReserveDetailAllReservation(serializers.Serializer):
    page = serializers.IntegerField()
    page_count = serializers.IntegerField()
    date = serializers.DateField()


class ReserveDetailAllReservationResponseSerializer(serializers.Serializer):
    pages = serializers.IntegerField()
    reserves = serializers.ListField(child=serializers.DictField())


class RemoveParticipantReserveSerializer(serializers.Serializer):
    reserve_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
