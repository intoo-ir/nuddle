from django.contrib.auth.backends import ModelBackend
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class MobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone_number = kwargs['phone_number']
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            pass


class EmailOrPhoneModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'phone_number': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
