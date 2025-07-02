from django.db import models

# Create your models here.
import uuid
from django.db import models

class Agent(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname

class Command(models.Model):
    TYPES = [
        ('UPGRADE_APPS', 'Upgrade apps'),
        ('UPDATE_OS', 'Update OS'),
        ('STOP_AGENT', 'Stop agent'),
    ]
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='commands')
    type = models.CharField(max_length=30, choices=TYPES)
    payload = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=15, default='pending', db_index=True)
    result = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Metric(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='metrics')
    cpu = models.FloatField()
    mem = models.FloatField()
    disk = models.FloatField()
    captured_at = models.DateTimeField()