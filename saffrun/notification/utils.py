from core.configs import Config
from najva_api_client.najva import Najva
from profile.models import UserProfile, EmployeeProfile
from rest_framework.pagination import PageNumberPagination

from .models import Notification


def add_token_to_user(user_profile: UserProfile, token: str):
    user_profile.notification_token = token
    user_profile.save()


def send_notif(employee: EmployeeProfile, _type: int, title: str, text: str, url: str):
    try:
        client = Najva()
        client.apikey = Config.najva_api_key
        client.token = Config.najva_token
        if _type == 1:
            followers_token = list(employee.followers.all().values_list("notification_token", flat=True))
            client.send_to_users(title, text, url,
                                 Config.saffrun_pic_url,
                                 followers_token)
            notif = Notification.objects.create(title=title, text=text, type=_type, sender=employee, url=url)
            notif.receivers.add(*list(UserProfile.objects.filter(following=employee).values_list("id", flat=True)))
            notif.save()

        elif _type == 2:
            client.send_to_all(title, text, url, Config.saffrun_pic_url)
            notif = Notification.objects.create(title=title, text=text, type=_type, sender=employee, url=url)
            notif.receivers.add(*list(UserProfile.objects.all().values_list("id", flat=True)))
            notif.save()
        return True
    except:
        return False


def get_all_sent_notification(employee: EmployeeProfile, page: int, page_count: int, request):
    paginator = PageNumberPagination()
    paginator.page_size = page_count
    paginator.page = page
    return paginator.paginate_queryset(employee.sent_notifications.all(), request), employee.sent_notifications.count()


def get_all_received_notification(client: UserProfile, page: int, page_count: int, request):
    paginator = PageNumberPagination()
    paginator.page_size = page_count
    paginator.page = page
    return paginator.paginate_queryset(client.received_notifications.all(), request)
