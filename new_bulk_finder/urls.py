# bulk_email_verifier/urls.py

from django.urls import path
from .views import BulkEmailfinderCreateView
# from .views import DownloadResultsView



urlpatterns = [
    path('find_emails_bulk/', BulkEmailfinderCreateView.as_view(), name='bulk-verify-emails'),
    # path('download-finder-results/', DownloadResultsView.as_view(), name='download_results'),
]

