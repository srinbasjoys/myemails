# bulk_email_verifier/serializers.py

from rest_framework import serializers
from .models import BulkEmailVerification

class BulkEmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkEmailVerification
        fields = '__all__'

