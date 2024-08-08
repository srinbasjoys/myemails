# bulk_email_verifier/serializers.py

from rest_framework import serializers
from .models import BulkEmailfinder

class BulkEmailfinderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkEmailfinder
        fields = '__all__'
