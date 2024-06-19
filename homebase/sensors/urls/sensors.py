from rest_framework import routers
from ..views import SensorViewSet


router = routers.SimpleRouter()
router.register(r"", SensorViewSet, basename="sensors")

urlpatterns = [] + router.urls