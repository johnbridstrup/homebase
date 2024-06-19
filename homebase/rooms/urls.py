from rest_framework import routers
from .views import RoomViewSet


router = routers.SimpleRouter()
router.register(r"", RoomViewSet, basename="rooms")

urlpatterns = [] + router.urls