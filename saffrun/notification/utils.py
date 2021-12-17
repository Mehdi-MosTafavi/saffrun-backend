from profile.models import UserProfile, EmployeeProfile
from najva_api_client.najva import Najva

from .models import Notification
from core.configs import Config


def add_token_to_user(user_profile: UserProfile, token: str):
    user_profile.notification_token = token
    user_profile.save()


def send_notif(employee: EmployeeProfile, _type: int, title: str, text: str, url: str):
    try:
        client = Najva()
        client.apikey = "63336392-f07c-48ed-9111-7d5f3b128b8d"
        client.token = "36c8a10b8f40441e51b21fb4568d511d42b80589"
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

def get_all_sent_notification(employee: EmployeeProfile):
    return employee.sent_notification.all()
