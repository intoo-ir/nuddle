from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify/', views.verify_view, name='verify'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
