from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions, views
from . import helper, serializers
from .serializers import UserSerializer, VerifyUserSerializer, UserUpdateSerializer, SetPasswordSerializer, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, UserLoginSerializer
from .models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import send_otp_task
from django.contrib.auth.tokens import default_token_generator

# from django_ratelimit.decorators import ratelimit
# from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    # @method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=True))
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        user, created = User.objects.get_or_create(phone_number=phone_number)
        # Calculate the time difference from the last OTP sent
        time_diff = timezone.now() - user.otp_creation_time if user.otp_creation_time else timezone.timedelta(
            seconds=121)

        if time_diff.total_seconds() < 120:
            return Response({"error": "OTP was recently sent. Please wait before requesting a new one."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
        # Generate and send a new OTP regardless of whether the user is new or existing
        otp = helper.get_random_otp()
        logger.debug(f'Generated OTP: {otp}')
        user.otp_code = otp
        user.otp_creation_time = timezone.now()  # Update the OTP creation time
        user.otp_status = 'generated'  # Update the OTP status to 'generated'
        user.save()

        # Send the OTP asynchronously using Celery
        send_otp_task.delay(phone_number, otp)  # Replace helper.send_otp with send_otp_task.delay

        # helper.send_otp(user.phone_number, otp)  # Send the OTP
        message = "New OTP sent." if not created else "OTP sent. Please verify to complete registration."
        return Response({"message": message}, status=status.HTTP_200_OK)


class VerifyUserView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyUserSerializer)
    def post(self, request, *args, **kwargs):
        """if request.user.is_authenticated:
            return Response({ 'User_Status': True})"""
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        user = get_object_or_404(User, phone_number=phone_number)
        if helper.verify_otp(user.phone_number, otp, user.otp_creation_time):
            user.is_active = True
            user.otp_status = 'used'
            user.user_type = 'free_user'
            # Update OTP status to 'used' after verification
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'Refresh_Token': str(refresh),
                'Access_Token': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "OTP is incorrect or expired"}, status=status.HTTP_400_BAD_REQUEST)


class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming the User model has a 'role' attribute; adjust as per your user model
        user_data = {
            "is_authenticated": request.user.is_authenticated,
            "username": request.user.phone_number,
        }
        return Response(user_data)


class CompleteRegistrationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Add this line

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=SetPasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Assuming the serializer validates the old password (if changing) and confirms the new password
            user = request.user
            user.password = make_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password set successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def post(self, request, *args, **kwargs):
        logger.debug("PasswordResetView: Received password reset request")
        serializer = PasswordResetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                logger.debug("PasswordResetView: Password reset instructions sent")
                return Response({"detail": "Password reset instructions have been sent."}, status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                logger.error(f"PasswordResetView: ValidationError - {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"PasswordResetView: Serializer errors - {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request, *args, **kwargs):
        logger.debug("PasswordResetConfirmView: Received password reset confirmation request")
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.debug("PasswordResetConfirmView: Password reset successfully")
            return Response(
                {"detail": "Your password has been reset successfully. Please log in with your new password."},
                status=status.HTTP_200_OK)
        else:
            logger.error(f"PasswordResetConfirmView: Serializer errors - {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.pk,
                'username': user.get_username(),
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming the User model has a 'role' attribute; adjust as per your user model
        user_data = {
            "profile_picture": request.user.profile_picture.url if request.user.profile_picture else None,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": request.user.phone_number,
            "email": request.user.email,

        }
        return Response(user_data)
