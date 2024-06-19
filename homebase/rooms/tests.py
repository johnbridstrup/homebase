from common.tests import BaseTest
from rooms.models import Room


class RoomTestCase(BaseTest):
    def test_get_rooms(self):
        Room.objects.create(name="Test Room")
        response = self.client.get("/rooms/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_room(self):
        response = self.client.post("/rooms/", {"name": "Test Room"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Test Room")
        self.assertEqual(response.data["id"], 1)
