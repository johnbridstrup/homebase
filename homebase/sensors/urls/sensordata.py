from rest_framework import routers
from ..views import SensorDataViewSet


router = routers.SimpleRouter()
router.register(r"", SensorDataViewSet, basename="sensordata")

urlpatterns = [] + router.urls