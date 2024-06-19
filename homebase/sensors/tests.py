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
