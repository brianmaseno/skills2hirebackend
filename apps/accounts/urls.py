"""
URL configuration for accounts app
"""
from django.urls import path
from .views import (
    UserRegistrationView,
    EmailVerificationView,
    UserProfileView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SimplePasswordResetCheckView,
    SimplePasswordResetView,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # Simple password reset (check if account exists, then allow password change)
    path('password/reset/check/', SimplePasswordResetCheckView.as_view(), name='password-reset-check'),
    path('password/reset/simple/', SimplePasswordResetView.as_view(), name='password-reset-simple'),
]
