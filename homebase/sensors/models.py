from django.db import models

from rooms.models import Room


class Sensor(models.Model):
    class SensorStatus(models.TextChoices):
        ACTIVE = 'AC', 'Active'
        INACTIVE = 'IN', 'Inactive'
        UNREGISTERED = 'UR', 'Unregistered'
    
    identifier = models.CharField(max_length=100, unique=True)  # Unique preferably UUID or serial no.
    name = models.CharField(max_length=100, null=True, blank=True)  # set after creation
    sensor_type = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='sensors')  # Set after creation
    status = models.CharField(max_length=2, choices=SensorStatus.choices, default=SensorStatus.UNREGISTERED)
    last_seen = models.DateTimeField(null=True, blank=True)

    def register(self, name):
        self.name = name
        self.status = self.SensorStatus.ACTIVE
        self.save()

    def add_to_room(self, room):
        self.room = room
        self.save()


# NOTE: Not sure how i want to handle auth here
# I think sensors will request connection and receive a token in order to authorize.
# They can do this on boot with their unique identifier.
class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
