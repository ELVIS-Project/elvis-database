from rest_framework.test import APITestCase
from elvis.tests.helpers import ElvisTestSetup
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from elvis.models.source import Source
from elvis.models.genre import Genre
from elvis.models.attachment import Attachment


class MovementTestCase(ElvisTestSetup, APITestCase):

    def setUp(self):
        self.setUp_user()

        self.p = Piece()
        self.p.creator = self.creator_user
        self.p.save()

        self.composer = Composer()
        self.composer.name = "Fake Composer"
        self.composer.save()

        self.m = Movement()
        self.m.creator = self.creator_user
        self.m.composer = self.composer
        self.m.title = "This is the movement title"
        self.m.save()

        self.source1 = Source()
        self.source1.title = "Source 1"
        self.source1.save()

        self.source2 = Source()
        self.source2.title = "Source 2"
        self.source2.save()

        self.genre1 = Genre()
        self.genre1.title = "Genre 1"
        self.genre1.save()

        self.genre2 = Genre()
        self.genre2.title = "Genre 2"
        self.genre2.save()

        self.attachment1 = Attachment()
        self.attachment1.description = "Attachment 1"
        self.attachment1.save()

        self.attachment2 = Attachment()
        self.attachment2.description = "Attachment 2"
        self.attachment2.save()

    def tearDown(self):
        self.p.delete()
        self.m.delete()
        self.composer.delete()
        self.source1.delete()
        self.source2.delete()
        self.genre1.delete()
        self.genre2.delete()
        self.attachment1.delete()

    def test_unicode(self):
        self.assertEqual(str(self.m), "This is the movement title")

    def test_sources(self):
        self.assertEqual(self.m.movement_sources(), "")
        # Add Source 1
        self.m.sources.add(self.source1)
        self.assertEqual(self.m.movement_sources(), "Source 1")
        # Add Source 2
        self.m.sources.add(self.source2)
        self.assertEqual(self.m.movement_sources(), "Source 1 Source 2")
        # Remove all
        self.m.sources.clear()
        self.assertEqual(self.m.movement_sources(), "")

    def test_genres(self):
        self.assertEqual(self.m.movement_genres(), "")
        # Add Genre 1
        self.m.genres.add(self.genre1)
        self.assertEqual(self.m.movement_genres(), "Genre 1")
        # Add Genre 2
        self.m.genres.add(self.genre2)
        self.assertEqual(self.m.movement_genres(), "Genre 1 Genre 2")
        # Remove all
        self.m.genres.clear()
        self.assertEqual(self.m.movement_genres(), "")

    def test_get_parent_cart_id(self):
        # No piece
        self.assertEqual(self.m.get_parent_cart_id, "")
        # Add the piece
        self.m.piece = self.p
        # Assert that it matches the regex
        self.assertRegexpMatches(self.m.get_parent_cart_id, self.uuid_regexp)
        # Remove it
        self.m.piece = None
        self.assertEqual(self.m.get_parent_cart_id, "")
