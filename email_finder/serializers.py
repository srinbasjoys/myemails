# email_finder/serializers.py
from rest_framework import serializers
from .models import EmailVerificationResult

class EmailVerificationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerificationResult
        fields = ('email', 'verification_status')

class EmailFinderInputSerializer(serializers.Serializer):
    fname = serializers.CharField(max_length=255)
    lname = serializers.CharField(max_length=255)
    domain = serializers.CharField(max_length=255)
