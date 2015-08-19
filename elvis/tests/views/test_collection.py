from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup
from elvis.models.collection import Collection


class CollectionViewTestCase(ElvisTestSetup, APITestCase):
    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()
        self.setUp_test_models()

    def test_get_list(self):
        response = self.client.get("/collections/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        collection = Collection.objects.filter(public=True)[0]
        response = self.client.get("/collection/{0}/".format(collection.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_id'], collection.id)