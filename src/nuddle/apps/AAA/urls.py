# AAA/urls.py

from django.urls import path
from .views import RegisterUserView, VerifyUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify/', VerifyUserView.as_view(), name='verify'),
    # ... other paths ...
]
