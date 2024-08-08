# email_verifier/models.py

from django.db import models

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    is_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    response_data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
