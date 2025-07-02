from rest_framework import serializers
from .models import Command

class HeartbeatSerializer(serializers.Serializer):
    hardware_uuid = serializers.CharField()
    hostname = serializers.CharField()
    version = serializers.CharField()
    cpu = serializers.FloatField()
    mem = serializers.FloatField()
    disk = serializers.FloatField()

class CommandResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    log = serializers.CharField(allow_blank=True)