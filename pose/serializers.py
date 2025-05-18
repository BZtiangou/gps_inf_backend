from rest_framework import serializers
from .models import PoseSource

class PoseSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoseSource
        fields = ['id', 'video', 'upload_date']
        read_only_fields = ['upload_date']
