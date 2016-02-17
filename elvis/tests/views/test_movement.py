from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup
from elvis.models.movement import Movement


class MovementViewTestCase(ElvisTestSetup, APITestCase):
    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()
        self.setUp_test_models()

    def test_get_list(self):
        response = self.client.get("/movements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        movement = Movement.objects.first()
        response = self.client.get("/movement/{0}/".format(movement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], str(movement.uuid))