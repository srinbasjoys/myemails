# email_finder/urls.py
from django.urls import path
from .views import EmailFinderView

urlpatterns = [
    path('single-find_email/', EmailFinderView.as_view(), name='find-email'),
]
        