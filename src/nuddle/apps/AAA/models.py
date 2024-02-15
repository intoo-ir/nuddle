from django.db import models
from django.contrib.auth.models import AbstractUser

from nuddle.apps.AAA.usermanager import UserManager


# Create your models here.
class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=13, unique=True)
    otp_code = models.PositiveIntegerField(blank=True, null=True)
    otp_creation_time = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = []

    backend = 'nuddle.apps.AAA.backend_auth.ModelBackend'
