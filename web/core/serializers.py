from rest_framework import serializers
from .models import Agent, Command, Metric, Inventory

# agents
class AgentSerializer(serializers.ModelSerializer):
    inventory = serializers.StringRelatedField(many=True)
    class Meta:
        model = Agent
        fields = '__all__'
# heartbeat
class HeartbeatSerializer(serializers.Serializer):
    hardware_uuid = serializers.CharField()
    hostname = serializers.CharField()
    version = serializers.CharField()
    cpu = serializers.FloatField()
    mem = serializers.FloatField()
    disk = serializers.FloatField()
    inventory = serializers.StringRelatedField(many=True)
# commands
class CommandResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    log = serializers.CharField(allow_blank=True)

class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = '__all__'

class CommandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ['agent', 'type', 'payload']
# metrics
class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = '__all__'
    
# inventory
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
