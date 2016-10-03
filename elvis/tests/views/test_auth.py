from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup, real_user, fake_user


class AuthViewTestCase(ElvisTestSetup, APITestCase):

    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()

    def tearDown(self):
        pass

    def test_authorized(self):
        can_log_in = self.client.login(username=real_user['username'],
                                       password=real_user['password'])
        self.assertTrue(can_log_in)
        self.client.logout()

    def test_unauthorized(self):
        can_log_in = self.client.login(username=fake_user['username'],
                                       password=fake_user['password'])
        self.assertFalse(can_log_in)

    def test_login_page_200(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        response = self.client.post('/login/', real_user)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.client.logout()

        response = self.client.post('/login/', fake_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        self.client.login(username=real_user['username'],
                          password=real_user['password'])
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
