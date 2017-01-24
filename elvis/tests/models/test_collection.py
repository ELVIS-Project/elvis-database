from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from elvis.tests.helpers import ElvisTestSetup
from elvis.models.collection import Collection
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.composer import Composer


class CollectionTestCase(ElvisTestSetup, APITestCase):

    def setUp(self):
        self.setUp_users()

        self.c = Collection()
        self.c.title = "This is the collection title"
        self.c.save()

        self.p = Piece()
        self.p.creator = self.creator_user
        self.p.save()

        self.composer = Composer()
        self.composer.name = "Fake Composer"
        self.composer.save()

        self.m = Movement()
        self.m.creator = self.creator_user
        self.m.composer = self.composer
        self.m.save()

    def tearDown(self):
        self.c.delete()
        self.p.delete()
        self.m.delete()
        self.composer.delete()

    def test_unicode(self):
        self.assertEqual(str(self.c), "This is the collection title")

    def test_add_piece(self):
        self.assertTrue(self.p not in self.c)
        self.assertEqual(self.c.piece_count, 0)
        self.c.add(self.p)
        self.assertEqual(self.c.piece_count, 1)
        self.assertEqual(self.p, self.c.pieces.first())
        self.assertTrue(self.p in self.c)

    def test_add_movement(self):
        self.assertTrue(self.m not in self.c)
        self.assertEqual(self.c.movement_count, 0)
        self.c.add(self.m)
        self.assertEqual(self.c.movement_count, 1)
        self.assertEqual(self.m, self.c.movements.first())
        self.assertTrue(self.m in self.c)

    def test_remove_piece(self):
        self.assertTrue(self.p not in self.c)
        self.c.add(self.p)
        self.assertTrue(self.p in self.c)
        self.c.remove(self.p)
        self.assertTrue(self.p not in self.c)

    def test_remove_movement(self):
        self.assertTrue(self.m not in self.c)
        self.c.add(self.m)
        self.assertTrue(self.m in self.c)
        self.c.remove(self.m)
        self.assertTrue(self.m not in self.c)

    def test_get_free_movements(self):
        # First test with a free movement
        self.assertListEqual(list(self.c.free_movements), [])
        self.assertEqual(self.c.free_movements_count, 0)
        self.c.add(self.m)
        self.assertListEqual(list(self.c.free_movements), [self.m])
        self.assertEqual(self.c.free_movements_count, 1)
        # Then, make self.m unfree and see that it responds
        self.m.piece = self.p
        self.p.movements.add(self.m)
        self.assertListEqual(list(self.c.free_movements), [])
        self.assertEqual(self.c.free_movements_count, 0)

    def test_container_contains_none(self):
        """
        Test that checking "None in collection" does not crash the program.
        Instead, it returns false.

        :return:
        """
        self.assertFalse(None in self.c)

    def test_invalid_contains_parameter(self):
        """
        Test that calling the __contains__ interface on Collection with an
        unacceptable parameter throws an exception.

        :return:
        """
        with self.assertRaises(Exception):
            5 in self.c
        with self.assertRaises(Exception):
            "bad" in self.c

    def test_maintain_valid_collection(self):
        """
        Test that a collection does not enter an invalid state when adding a
        movement or piece such that the movement is in the piece.

        An invalid state is when a collection contains both the movement and the
        piece even though the movement is contained within the piece.

        :return:
        """
        # M is a movement in P
        self.m.piece = self.p
        self.p.movements.add(self.m)
        # Neither M or P is in C
        self.assertTrue(self.m not in self.c)
        self.assertTrue(self.p not in self.c)
        # Only M is in C
        self.c.add(self.m)
        self.assertTrue(self.m in self.c)
        self.assertTrue(self.p not in self.c)
        # Add P to C, thereby removing just M
        self.c.add(self.p)
        self.assertTrue(self.m not in self.c)
        self.assertTrue(self.p in self.c)
        # Try to add just M.  M remains not in C and P remains in C
        self.c.add(self.m)
        self.assertTrue(self.m not in self.c)
        self.assertTrue(self.p in self.c)
