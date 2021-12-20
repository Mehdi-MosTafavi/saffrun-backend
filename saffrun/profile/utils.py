from profile.models import EmployeeProfile, UserProfile


def remove_follower_user(user: UserProfile, employee: EmployeeProfile):
    employee.followers.remove(user)
