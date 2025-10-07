from django.urls import path
from .views import (
    LoginView, RoleListCreateView, UserListView, 
    CurrentUserView, Enable2FAView, Verify2FAView,
    Toggle2FAView, PasswordResetRequestView, PasswordResetConfirmView,
    VerifyOTPView, ChangePasswordView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('roles/', RoleListCreateView.as_view(), name='roles'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('2fa/enable/', Enable2FAView.as_view(), name='enable-2fa'),
    path('2fa/verify/', Verify2FAView.as_view(), name='verify-2fa'),
    path('2fa/toggle/', Toggle2FAView.as_view(), name='toggle-2fa'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<int:user_id>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]


