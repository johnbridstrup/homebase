from django.db import models
from rest_framework import serializers

from .models import Sensor, SensorData


class SensorSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(write_only=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Sensor
        fields = ["id", "name", "room", "sensor_type", "identifier", "status", "last_seen"]
        read_only_fields = ["id"]


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ["id", "sensor", "data", "timestamp"]
        read_only_fields = ["id", "timestamp"]