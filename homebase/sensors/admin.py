from django.contrib import admin

from .models import Sensor, SensorData


class SensorAdmin(admin.ModelAdmin):
    list_display = ("name", "room", "sensor_type", "identifier", "status", "last_seen")
    search_fields = (
        "name",
        "room__name",
    )


class SensorDataAdmin(admin.ModelAdmin):
    list_display = ("sensor", "data", "timestamp")
    search_fields = (
        "sensor__name",
    )

admin.site.register(Sensor, SensorAdmin)
admin.site.register(SensorData, SensorDataAdmin)
