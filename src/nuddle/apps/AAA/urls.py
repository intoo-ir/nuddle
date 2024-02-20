# AAA/urls.py

from django.urls import path
from .views import RegisterUserView, VerifyUserView, UserStatusView, CompleteRegistrationView, SetPasswordView, PasswordResetView, PasswordResetConfirmView, UserLoginView, UserProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify/', VerifyUserView.as_view(), name='verify'),
    path('user_status/', UserStatusView.as_view(), name='user-status'),
    path('set_password/', SetPasswordView.as_view(), name='set-password'),
    path('forget_password/', PasswordResetView.as_view(), name='password_reset'),
    path('forget_password_confirmation/', PasswordResetConfirmView.as_view(), name='forget_password_confirmation'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('complete_registration/', CompleteRegistrationView.as_view(), name='Complete_Registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token_refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token_verify/', TokenVerifyView.as_view(), name='token_verify'),
    # ... other paths ...
]
