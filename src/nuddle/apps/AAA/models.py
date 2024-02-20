from django.db import models
from django.contrib.auth.models import AbstractUser
from nuddle.apps.AAA.usermanager import UserManager
from django.utils import timezone
from django.core.validators import EmailValidator


# Create your models here.
class User(AbstractUser):
    username = None  # Remove username as a required field
    phone_number = models.CharField(max_length=13, unique=True)
    otp_code = models.PositiveIntegerField(blank=True, null=True)
    otp_creation_time = models.DateTimeField(auto_now=True)
    otp_status = models.CharField(max_length=10, default='generated',
                                  choices=(('generated', 'Generated'), ('used', 'Used')))
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True, validators=[EmailValidator()])
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    user_type = models.CharField(max_length=50, choices=(
        ('subscriber', 'Subscriber'), ('free_user', 'Free User')),
                                 default='free_user')
    status = models.CharField(max_length=50,
                              choices=(('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended')),
                              default='inactive')

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    backend = 'nuddle.apps.AAA.backend_auth.ModelBackend'
