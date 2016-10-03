from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup, real_user
from elvis.models.composer import Composer


class DownloadViewTestCase(ElvisTestSetup, APITestCase):
    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()
        self.setUp_test_models()

        self.client.login(username=real_user['username'], password=real_user['password'])

    def tearDown(self):
        self.client.logout()

    def test_get_clear_collection(self):
        response = self.client.post("/download-cart/",
                                    data={"clear-collection":""})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_check_in_cart(self):
    #     response = self.client.post("/download-cart/",
    #                                 data={"check_in_cart":""})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
