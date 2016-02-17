# from rest_framework.test import APITestCase
# from rest_framework import status
# from elvis.tests.helpers import ElvisTestSetup
# from elvis.models.composer import Composer
#
#
# class ComposerViewTestCase(ElvisTestSetup, APITestCase):
#     def setUp(self):
#         self.setUp_elvis()
#         self.setUp_user()
#         self.setUp_test_models()
#
#     def test_get_list(self):
#         response = self.client.get("/composers/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_get_detail(self):
#         composer = Composer.objects.first()
#         response = self.client.get("/composer/{0}/".format(composer.id))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['id'], composer.id)