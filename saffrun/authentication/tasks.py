from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import validate_email
from saffrun.celery import app
from saffrun.settings import EMAIL_HOST_USER


@app.task(bind=True)
def send_email(self, *args):
    user = User.objects.get(username=args[0])
    new_password = User.objects.make_random_password()
    user.set_password(new_password)
    user.save()
    if not validate_email(user.email):
        raise Exception('Email InValid')
    send_mail('New Password', f'Hi {user.username}!\nYour new password is: {new_password}', EMAIL_HOST_USER,
              recipient_list=[user.email], fail_silently=False)
