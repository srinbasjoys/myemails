# email_finder/models.py
from django.db import models

class EmailVerificationResult(models.Model):
    email = models.EmailField(unique=True)
    verification_status = models.CharField(max_length=255)

    def __str__(self):
        return self.email
