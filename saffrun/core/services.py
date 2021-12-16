from django.contrib.auth.models import User


def is_user_employee(user: User) -> bool:
    try:
        user.employee_profile
        return True
    except:
        return False

def is_user_client(user: User) -> bool:
    try:
        user.user_profile
        return True
    except:
        return False