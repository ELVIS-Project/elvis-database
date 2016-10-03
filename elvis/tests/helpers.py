from django.contrib.auth.models import User
from django.test import Client
from model_mommy import mommy
from django.test import override_settings
from rest_framework.test import APITestCase

# Some user accounts to use for testing
real_user = {
    'username': 'testuser',
    'password': 'test'
}
fake_user = {
    'username': 'fake',
    'password': 'fake'
}
creator_user = {
    'username': 'creatoruser',
    'password': 'test'
}

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
        self.test_user = User.objects.create_user(username=real_user['username'], password=real_user['password'])
        self.creator_user = User.objects.create_user(username=creator_user['username'], password=creator_user['password'])
        self.super_user = User.objects.create_superuser(username='superuser', email='a@g.com', password='test')
