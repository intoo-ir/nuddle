# AAA/serializers.py
from rest_framework import serializers
from django.contrib.auth.forms import PasswordResetForm
from .models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']  # Assuming you're including otp_code in the serializer for completeness

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        # Check if user already exists
        user, created = User.objects.get_or_create(phone_number=phone_number)
        if not created:
            # If the user exists, update the otp_code and otp_creation_time
            user.otp_code = validated_data.get('otp_code', user.otp_code)  # Optionally generate a new OTP here instead
            user.otp_creation_time = timezone.now()
            user.save(update_fields=['otp_code', 'otp_creation_time'])
        return user


class VerifyUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.IntegerField()


    def validate(self, data):
        """
        Check that the OTP is valid for the given phone number.
        """
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        try:
            user = User.objects.get(phone_number=phone_number, otp_code=otp)
            # Optionally, verify OTP expiration here as well
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid phone number or OTP.")
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(allow_null=True, required=False)  # Explicitly define the field

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_picture']


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        # Check that the two password fields match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords must match.")
        return data


class PasswordResetSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()

    def validate_email_or_phone(self, value):
        logger.debug(f"Validating email or phone: {value}")
        if "@" in value:  # Assume it's an email
            users = User.objects.filter(email=value)
            if not users.exists():
                logger.error(f"No user found with email: {value}")
                raise serializers.ValidationError("A user with this email does not exist.")
        else:  # Assume it's a phone number
            users = User.objects.filter(phone_number=value)
            if not users.exists():
                logger.error(f"No user found with phone number: {value}")
                raise serializers.ValidationError("A user with this phone number does not exist.")
            if not users.filter(email__isnull=False).exists():
                logger.warning(f"User with phone number {value} has no email associated")
                raise serializers.ValidationError(
                    "You don't have an email information on your profile. Please use the SMS OTP method to login and add email information in your profile page.")
        return value

    def save(self, **kwargs):
        data = self.validated_data['email_or_phone']
        logger.debug(f"Attempting to save password reset data for: {data}")
        request = self.context.get('request')
        if "@" in data:
            # It's an email
            form = PasswordResetForm({'email': data})
        else:
            # It's a phone number, find the user's email
            user = User.objects.get(phone_number=data)
            form = PasswordResetForm({'email': user.email})

        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
                'email_template_name': 'index-fa-forget-password.html',
                'request': request,
                'html_email_template_name': 'index-fa-forget-password.html',
            }
            form.save(**opts)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
            logger.debug(f"Decoded UID: {uid}, User ID: {user.pk}, User: {user.phone_number}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Error decoding UID or user not found: {e}")
            raise serializers.ValidationError({'uidb64': ['Invalid token or user does not exist.']})

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({'uidb64': ['Invalid token or user does not exist.']})

        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': ['The two password fields didn’t match.']})

            # Store the user in the validated_data to use it in the save method
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']  # Retrieve the user from the validated data
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("email_or_phone")
        password = data.get("password")

        if username and password:
            # Support login with either email or phone number
            if '@' in username:
                user = authenticate(email=username, password=password)
            else:
                user = authenticate(phone_number=username, password=password)

            if user:
                if not user.is_active:
                    msg = "User account is disabled."
                    raise serializers.ValidationError(msg)
                data["user"] = user
                return data
            else:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg)
        else:
            msg = "Must include both username and password."
            raise serializers.ValidationError(msg)
