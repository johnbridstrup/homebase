from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rooms.models import Room
from .models import Sensor, SensorData
from .serializers import SensorSerializer, SensorDataSerializer


class SensorViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    serializer_class = SensorSerializer
    queryset = Sensor.objects.all()

    def create(self, request, *args, **kwargs):
        sensor_ident = request.data.get("identifier")
        sensor_type = request.data.get("sensor_type")

        sensor, created = Sensor.objects.get_or_create(identifier=sensor_ident, sensor_type=sensor_type)
        return Response(
            self.serializer_class(sensor).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    
    @action(
        methods=["post"],
        detail=True,
        url_path="register",
        renderer_classes=[
            JSONRenderer,
        ],
    )
    def register_sensor(self, request, pk=None):
        sensor = self.get_object()
        room = request.data.get("room")
        print(request.data)
        if isinstance(room, list):
            if len(room) == 1:
                room = room[0]
            else:
                raise ValueError("Only assign one room")
        sensor.register(request.data.get("name"))
        if room is not None:
            room_obj = Room.objects.get(id=room)
            sensor.add_to_room(room_obj)
        return Response(self.serializer_class(sensor, context={"request": request}).data, status=status.HTTP_200_OK)
    
    @action(
        methods=["get"],
        detail=True,
        url_path="data",
        renderer_classes=[
            JSONRenderer,
        ],
    )
    def get_data(self, request, pk=None):
        sensor = self.get_object()
        filts = {}
        if "start" in request.query_params:
            filts["timestamp__gte"] = request.query_params["start"]
        if "end" in request.query_params:
            filts["timestamp__lte"] = request.query_params["end"]
        data = sensor.data.filter(**filts)
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            return self.get_paginated_response(SensorDataSerializer(paginated_data, many=True, context={"request": request}).data)
        return Response(SensorDataSerializer(data, many=True).data)


class SensorDataViewSet(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    serializer_class = SensorDataSerializer
    queryset = SensorData.objects.all()

    def create(self, request, *args, **kwargs):
        sensor_ident = request.data.get("identifier")
        data = request.data.get("data")
        sensor = Sensor.objects.get(identifier=sensor_ident)
        if sensor.status != Sensor.SensorStatus.ACTIVE:
            return Response(
                {"error": "Sensor is not active"},
                status=status.HTTP_403_FORBIDDEN,
            )
        request.data["sensor"] = sensor.id
        request.data["data"] = data
        return super().create(request, *args, **kwargs)
