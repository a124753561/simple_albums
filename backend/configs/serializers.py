from rest_framework import serializers
from .models import SystemConfig


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ["id", "key", "value", "description"]
