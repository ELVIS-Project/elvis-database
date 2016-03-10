from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup, real_user, fake_user


class CommonPublicViewTestCase(ElvisTestSetup, APITestCase):
    """
    This class makes a get request to all of the common URLs and makes
    sure that they all return 200-OK.
    """

    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()

    def tearDown(self):
        pass

    # Static pages

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_about(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact(self):
        response = self.client.get("/contact/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suggest(self):
        response = self.client.get("/suggest/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Search Engine

    def test_search(self):
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_add_to_cart(self):
        response = self.client.get("/search/add-to-cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Account Management Pages

    def test_account(self):
        response = self.client.get("/account/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_update(self):
        response = self.client.get("/account/update/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_password_change(self):
        self.__test_get_private_url("/account/password_change/",
                                status.HTTP_302_FOUND,
                                status.HTTP_200_OK)

    def test_account_password_change_done(self):
        self.__test_get_private_url("/account/password_change_done/",
                                status.HTTP_302_FOUND,
                                status.HTTP_200_OK)

    def test_register(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Password Management Pages

    def test_password_reset(self):
        response = self.client.get("/password/reset/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_done(self):
        response = self.client.get("/password/reset/done/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_complete(self):
        response = self.client.get("/password/reset/complete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Download Pages

    def test_downloading(self):
        self.__test_get_private_url("/downloading/",
                                    status.HTTP_403_FORBIDDEN,
                                    status.HTTP_200_OK)

    def test_download_cart(self):
        self.__test_get_private_url("/download-cart/",
                                    status.HTTP_403_FORBIDDEN,
                                    status.HTTP_200_OK)

    # Pieces

    def test_pieces(self):
        response = self.client.get("/pieces/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_pieces_upload(self):
    #     self.__test_get_private_url("/pieces-upload/",
    #                             status.HTTP_404_NOT_FOUND,
    #                             status.HTTP_200_OK)

    # Collections

    def test_collections(self):
        response = self.client.get("/collections/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_collection_create(self):
        self.__test_get_private_url("/collection/create/",
                                    status.HTTP_302_FOUND,
                                    status.HTTP_200_OK)

    # Composers

    def test_composers(self):
        response = self.client.get("/composers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Users

    def test_users(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Movements

    def test_movements(self):
        response = self.client.get("/movements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def __test_get_private_url(self, url, logged_out_status, logged_in_status):
        """
        Get a URL as both a logged-out and logged-in user.  Assert that the
        logged-out and logged-in users get the proper HTTP status code.

        :param url:
        :param logged_out_status:
        :param logged_in_status:
        :return:
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, logged_out_status)
        # Make sure users can access
        self.client.login(username=real_user['username'],
                          password=real_user['password'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, logged_in_status)
        # Logout, then make sure we lose access again
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, logged_out_status)
