from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import helper
from .serializers import UserSerializer, VerifyUserSerializer
from .models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        user, created = User.objects.get_or_create(phone_number=phone_number)
        if not created:
            # User exists, so generate and send a new OTP
            otp = helper.get_random_otp()
            logger.debug(f'Generated OTP: {otp}')
            user.otp_code = otp
            user.otp_creation_time = timezone.now()
            user.save(update_fields=['otp_code', 'otp_creation_time'])
            #helper.send_otp(phone_number, otp)  # Assuming this function is correctly implemented
            return Response({"message": "New OTP sent."}, status=status.HTTP_200_OK)
        else:
            # New user registration logic here (similar to your existing logic)
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                otp = helper.get_random_otp()
                logger.debug(f'Generated OTP: {otp}')
                user.otp_code = otp
                user.otp_creation_time = timezone.now()
                user.save(update_fields=['otp_code', 'otp_creation_time'])
                #helper.send_otp(phone_number, otp)
                return Response({"message": "User registered and OTP sent."}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyUserView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyUserSerializer)
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        user = get_object_or_404(User, phone_number=phone_number)
        if helper.verify_otp(user.phone_number, otp):
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'Refresh_Token': str(refresh),
                'Access_Token': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "OTP is incorrect or expired"}, status=status.HTTP_400_BAD_REQUEST)


