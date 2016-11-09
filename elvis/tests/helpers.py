from django.contrib.auth.models import User
from django.test import Client
from django.test import override_settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from elvis.models import UserProfile
# Some user accounts to use for testing
test_users = [
    {
        'username': 'test_user',
        'accepted_tos': True
    },
    {
        'username': 'creator_user',
        'accepted_tos': True
    },
    {
        'username': 'super_user',
        'email': 'a@b.com',
        'accepted_tos': True,
        'is_superuser': True
    },
    {
        'username': 'no_tos_user',
    }
]

real_user = test_users[0]
fake_user = {'username': 'fake', 'password': 'fake'}
creator_user = test_users[1]


@override_settings(SOLR_SERVER="http://localhost:8983/solr/elvisdb_test")
class ElvisTestSetup(APITestCase):

    uuid_regexp = r"P-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"

    def url(self, obj):
        model_name = obj.__class__.__name__.lower()
        return "http://localhost:8000/{0}/{1}".format(model_name, obj.id)

    def setUp_elvis(self):
        self.client = Client()

    def setUp_test_models(self):
        self.test_composer = mommy.make('elvis.Composer')
        self.test_piece = mommy.make('elvis.Piece', composer=self.test_composer, uploader=self.creator_user)
        self.test_hidden_piece = mommy.make('elvis.Piece', composer=self.test_composer, uploader=self.creator_user, hidden=True)
        self.test_movement = mommy.make('elvis.Movement', composer=self.test_composer, uploader=self.creator_user)
        self.test_hidden_movement = mommy.make('elvis.Movement', composer=self.test_composer, uploader=self.creator_user, hidden=True)
        self.test_collection = mommy.make('elvis.Collection', public=True)
        self.test_private_collection = mommy.make('elvis.Collection', public=False, creator=self.creator_user)

    def setUp_user(self):
        """Set up users for the test suite to use.

        Here we explicitly create UserProfiles for the users and set their
        accepted_tos values manually in order to avoid relying on the correct
        functioning of the UserForm.
        """

        for user_info in test_users:
            if user_info.get('is_superuser'):
                user = User.objects.create_superuser(username=user_info['username'],
                                                     email=user_info['email'],
                                                     password='test')
            else:
                user = User.objects.create_user(username=user_info['username'],
                                                password='test')
            user_profile = UserProfile(user=user)
            if user_info.get('accepted_tos'):
                user_profile.accepted_tos = True
            user_profile.save()

            # Assign each user to an attribute name based on their username.
            setattr(self, user_info['username'], user)
