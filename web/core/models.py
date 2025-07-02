import uuid
from django.db import models
from django.db.models import DateTimeField, Func
from django.utils import timezone

class Agent(models.Model):
    uuid = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    hardware_uuid = models.CharField(unique=True, default="")
    hostname = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname
    
    class Meta:
        ordering = ("-last_seen",)

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

class TruncDay(Func):
    function = 'date_trunc'
    template = "%(function)s('day', %(expressions)s)"


class Metric(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='metrics')
    cpu = models.FloatField()
    mem = models.FloatField()
    disk = models.FloatField()
    captured_at = models.DateTimeField()
    # class Meta:
    #     unique_together = (
    #         ("agent", "day_bucket"),
    #     )

    # # champ virtuel stocké (requires migrations)
    # day_bucket = DateTimeField(editable=False)

    # def save(self, *args, **kwargs):
    #     self.day_bucket = self.captured_at.replace(hour=0, minute=0,
    #                                                second=0, microsecond=0)
    #     super().save(*args, **kwargs)