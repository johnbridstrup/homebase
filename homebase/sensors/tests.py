import uuid

from common.tests import BaseTest
from rooms.models import Room
from sensors.models import Sensor, SensorData


class SensorTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.room = Room.objects.create(name="Test Room")

    def create_sensor(self, sensor_type="Test Type"):
        ident = str(uuid.uuid4())
        return Sensor.objects.create(
            identifier=ident,
            sensor_type=sensor_type,
        )

    def test_basic(self):
        sensor = self.create_sensor()
        self.assertEqual(sensor.sensor_type, "Test Type")
        self.assertEqual(sensor.status, Sensor.SensorStatus.UNREGISTERED)
        self.assertIsNone(sensor.last_seen)

    def test_register(self):
        sensor = self.create_sensor()
        self.assertEqual(sensor.status, Sensor.SensorStatus.UNREGISTERED)
        sensor.register("Test Sensor", self.room)
        self.assertEqual(sensor.name, "Test Sensor")
        self.assertEqual(sensor.status, Sensor.SensorStatus.ACTIVE)

    def test_sensor_data(self):
        sensor = self.create_sensor()
        sensor.register("Test Sensor", self.room)
        SensorData.objects.create(sensor=sensor, data={"temperature": 25})
        self.assertEqual(sensor.data.count(), 1)
        self.assertEqual(sensor.data.first().data, {"temperature": 25})
        self.assertIsNotNone(sensor.data.first().timestamp)
    
    def test_api_get_sensors(self):
        sensor = self.create_sensor()
        sensor.register("Test Sensor", self.room)
        response = self.client.get("/sensors/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], sensor.id)
        self.assertEqual(response.data["results"][0]["status"], Sensor.SensorStatus.ACTIVE.label)
    
    def test_api_create_sensor(self):
        UUID = str(uuid.uuid4())
        response = self.client.post("/sensors/", {"identifier": UUID, "sensor_type": "Test Type"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Sensor.objects.count(), 1)
        self.assertEqual(Sensor.objects.first().sensor_type, "Test Type")
        sensor = Sensor.objects.first()
        
        r2 = self.client.get(f"/sensors/{sensor.id}/")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.data["id"], sensor.id)
        self.assertEqual(r2.data["status"], Sensor.SensorStatus.UNREGISTERED.label)

        sensor.register("Test Sensor", self.room)
        r3 = self.client.get(f"/sensors/{sensor.id}/")
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.data["id"], sensor.id)
        self.assertEqual(r3.data["status"], Sensor.SensorStatus.ACTIVE.label)

        r4 = self.client.post("/sensors/", {"identifier": UUID, "sensor_type": "Test Type"})
        self.assertEqual(r4.status_code, 200)
        self.assertEqual(Sensor.objects.count(), 1)
        self.assertEqual(Sensor.objects.first().sensor_type, "Test Type")
        self.assertEqual(r4.data["status"], Sensor.SensorStatus.ACTIVE.label)
    
    def test_api_create_sensor_data(self):
        sensor = self.create_sensor()
        response = self.client.post("/sensordata/", {"identifier": sensor.identifier, "data": {"temperature": 25}}, format="json")
        # Fails if not registered
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SensorData.objects.count(), 0)

        sensor.register("Test Sensor", self.room)
        response = self.client.post("/sensordata/", {"identifier": sensor.identifier, "data": {"temperature": 25}}, format="json")
        # Succeeds
        self.assertEqual(SensorData.objects.count(), 1)
        self.assertEqual(SensorData.objects.first().data, {"temperature": 25})

    def test_api_register_sensor(self):
        sensor = self.create_sensor()
        response = self.client.post(f"/sensors/{sensor.id}/register/", {"name": "Test Sensor", "room": self.room.id}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Sensor.SensorStatus.ACTIVE.label)
        self.assertEqual(response.data["name"], "Test Sensor")
        self.assertEqual(response.data["room"], self.room.id)
