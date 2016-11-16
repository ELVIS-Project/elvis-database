from rest_framework.test import APITestCase
from rest_framework import status
from model_mommy import mommy
from elvis.tests.helpers import ElvisTestSetup
from elvis.models.composer import Composer
import pdb


class ComposerViewTestCase(ElvisTestSetup, APITestCase):

    def setUp(self):
        self.test_composer = mommy.make('elvis.Composer')

    def test_get_list(self):
        """
        Query the API for the list of composers.  Check that it returns 200.
        """
        response = self.client.get("/composers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        """
        Query the API for the details of a composer.  Check that API returns the
        correct UUID.
        """
        composer = Composer.objects.first()
        response = self.client.get("/composer/{0}/".format(composer.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], str(composer.uuid))
