from profile.models import UserProfile, EmployeeProfile
from najva_api_client.najva import Najva

from .models import Notification


def add_token_to_user(user_profile: UserProfile, token: str):
    user_profile.notification_token = token
    user_profile.save()


def send_notif(employee: EmployeeProfile, _type: int, title: str, text: str):
    try:
        client = Najva()
        client.apikey = "63336392-f07c-48ed-9111-7d5f3b128b8d"
        client.token = "36c8a10b8f40441e51b21fb4568d511d42b80589"
        if _type == 1:
            followers_token = list(employee.followers.all().values_list("notification_token", flat=True))
            client.send_to_users()(title=title, body=text, subscriber_tokens=followers_token)
            Notification.objects.create(title=title, text=text, type=_type,
                                        receivers=UserProfile.objects.filter(following=employee))
        elif _type == 2:
            client.send_to_all(title=title, body=text)
            Notification.objects.create(title=title, text=text, type=_type,
                                        receivers=UserProfile.objects.all())
        return True
    except:
        return False
