from django.test.client import MULTIPART_CONTENT
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
        self.assertEqual(response.data['id'], collection.id)

    def test_get_private_detail(self):
        collection = Collection.objects.filter(public=False)[0]
        self.client.login(username='testuser', password='test')
        response = self.client.get("/collection/{0}/".format(collection.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        self.client.login(username='creatoruser', password='test')
        response = self.client.get("/collection/{0}/".format(collection.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], collection.id)
        self.client.logout()

    def test_get_download_cart_not_allowed(self):
        response = self.client.get("/download-cart/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_download_cart_allowed(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get("/download-cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def update_collection_not_allowed(self):
        collection = Collection.objects.filter(public=False)[0]
        response = self.client.post('/collections/', {'action': 'make-public',
                                                      'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post('/collections/', {'action': 'make-private',
                                                      'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post('/collections/', {'action': 'delete',
                                                      'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='testuser', password='test')
        response = self.client.post('/collections/', {'action': 'make-public',
                                                      'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        response = self.client.post('/collections/', {'action': 'make-private',
                                                      'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post('/collections/', {'action': 'delete',
                                                      'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def update_collection_allowed(self):
        collection = Collection.objects.filter(public=False)[0]
        self.client.login(username='creatoruser', password='test')
        response = self.client.post('/collections/', {'action': 'make-public', 'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response = self.client.post('/collections/', {'action': 'make-private', 'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response = self.client.post('/collections/', {'action': 'nonesense', 'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post('/collections/', {'action': 'delete', 'id': collection.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response = self.client.post('/collections/', {'title': 'Test', 'comment': 'Test', 'creator': self.creator_user})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_invalid_collection_create(self):
        """
        Test creating an invalid collection through the API.

        :return:
        """
        # Test an invalid input
        response = self.client.post("/collections/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_collection_create(self):
        """
        Test creating a valid collection through the API.

        :return:
        """
        self.client.login(username='creatoruser', password='test')
        # Test a valid input
        response = self.client.post("/collections/", data={
            "title": "A am a test collection 12345",
            "comment": "A nice comment",
            "permission": "Public"
        })
        # 302 because we're redirected to the existing collection
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        # Test a valid private input
        response = self.client.post("/collections/", data={
            "title": "A private collection",
            "comment": "A nice comment",
            "permission": "Private",
            "initialize_empty": False
        })
        # 302 because we're redirected to the existing collection
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        # Get the new collection.  By default the url doesn't have trailing
        # slash, so we add one
        response = self.client.get("{0}/".format(response.url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        collection = response.data
        # Now, we will try to update the collection
        response = self.client.patch("/collection/{0}/".format(collection["id"]),
         data={
            "title": "the new title",
            "comment": "the new comment!!!"
        })
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_collection_create_page(self):
        """
        Test that the collection creation form loads.
        """
        # First, try to load it not logged in
        response = self.client.get("/collection/create/")
        # 302 because we're redirected to the login page
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        # Now log in and try correctly
        self.client.login(username="creatoruser", password="test")
        response = self.client.get("/collection/create/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
