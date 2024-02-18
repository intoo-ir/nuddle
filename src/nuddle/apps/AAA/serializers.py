# AAA/serializers.py
from rest_framework import serializers
from .models import User
from django.utils import timezone


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
