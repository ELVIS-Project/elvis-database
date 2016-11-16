from rest_framework.test import APITestCase
from elvis.tests.helpers import ElvisTestSetup
from elvis.forms import UserForm


class UserFormTestCase(ElvisTestSetup, APITestCase):

    def setUp(self):
        self.setUp_users()

    def test_save_user(self):
        form = UserForm()
        form.email = "test@test.com"
        form.first_name = "Bob"
        form.last_name = "L'Eponge"
        form.password1 = "pass1"
        form.password2 = "pass2"
        # form.save(True)
