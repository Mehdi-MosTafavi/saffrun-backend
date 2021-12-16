
from profile.models import UserProfile


def add_token_to_user(user_profile: UserProfile, token: str):
    user_profile.notification_token = token
    user_profile.save()