# email_verifier/urls.py

from django.urls import path
from .views import EmailVerificationListCreateView

urlpatterns = [
    path('single-verify-email/', EmailVerificationListCreateView.as_view(), name='email-verification'),
]
