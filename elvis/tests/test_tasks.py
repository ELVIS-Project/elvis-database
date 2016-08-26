import os
from rest_framework.test import APITestCase
from elvis.tests.helpers import ElvisTestSetup
from elvis.tasks import rebuild_suggester_dicts, delete_zip_file, CartZipper, \
    zip_files
from elvis.settings import BASE_DIR


class TasksTestCase(ElvisTestSetup, APITestCase):
    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()
        self.setUp_test_models()

    def test_rebuild_suggester_dicts(self):
        rebuild_suggester_dicts.delay()

    def test_zip_files(self):
        # path = BASE_DIR + "/test_zip.zip"
        # self.assertFalse(os.path.isfile(path))
        zip_files.delay({
            "keys": [2]
        }, [], self.creator_user.username, True)
        # For some reason, zip_files() breaks every other test
        # pass
    #
    # def test_create_zip_file(self):
    #     cart_zipper = CartZipper("/test_temp/", [], [], self.creator_user.username)

    def test_delete_zip_file(self):
        """
        Create a test zip, and then try to delete it
        :return:
        """
        path = BASE_DIR + "/test_zip.zip"
        self.assertFalse(os.path.isfile(path))
        f = open(path, "w")
        f.write("blahblah")
        f.close()
        self.assertTrue(os.path.isfile(path))
        delete_zip_file.delay(path)