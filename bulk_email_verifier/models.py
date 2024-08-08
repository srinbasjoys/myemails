# bulk_email_verifier/models.py

from django.db import models
import uuid

class BulkEmailVerification(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    download_url = models.URLField(blank=True, null=True)

    file_id = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return str(self.file_id)

    
