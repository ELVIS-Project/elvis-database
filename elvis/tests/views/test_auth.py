from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup

class AuthViewTestCase(ElvisTestSetup, APITestCase):
    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()

    def test_authorized(self):
        can_log_in = self.client.login(username='testuser', password='test')
        self.assertTrue(can_log_in)
        self.client.logout()

    def test_unauthorized(self):
        can_log_in = self.client.login(username='fake', password='fake')
        self.assertFalse(can_log_in)

    def test_login(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.client.logout()

        response = self.client.post('/login/', {'username': 'fake', 'password': 'fake'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)