from django.contrib.auth.backends import ModelBackend
from .models import User


class MobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone_number = kwargs['phone_number']
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            pass
