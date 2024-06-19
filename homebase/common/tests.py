from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient


class BaseTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user")
        self.client = APIClient()

    def tearDown(self) -> None:
        return super().tearDown()
