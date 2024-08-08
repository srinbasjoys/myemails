# bulk_email_verifier/urls.py

from django.urls import path
from .views import BulkEmailVerificationCreateView
# from .views import DownloadResultsView



urlpatterns = [
    path('bulk-verify-emails/', BulkEmailVerificationCreateView.as_view(), name='bulk-verify-emails'),
    # path('bulk-verify-results/', DownloadResultsView.as_view(), name='download_results'),
]

