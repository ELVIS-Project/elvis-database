from rest_framework.test import APITestCase
from rest_framework import status
from elvis.tests.helpers import ElvisTestSetup
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.collection import Collection
from elvis.models.genre import Genre
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.language import Language
from elvis.models.location import Location
from elvis.models.source import Source
from elvis.models.tag import Tag


class CollectionViewTestCase(ElvisTestSetup, APITestCase):
    def setUp(self):
        self.setUp_elvis()
        self.setUp_user()
        self.setUp_test_models()

    def test_get_list(self):
        response = self.client.get("/pieces/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_user_slice(self):
        response = self.client.get("/pieces/", {'creator': self.creator_user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        piece = Piece.objects.first()
        response = self.client.get("/piece/{0}/".format(piece.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], piece.id)

    # def test_get_update_not_allowed(self):
    #     piece = Piece.objects.first()
    #     self.client.login(username='testuser', password='test')
    #     response = self.client.get("/piece/{0}/update/".format(piece.id))
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.client.logout()

    def test_get_update_allowed(self):
        piece = Piece.objects.first()
        self.client.login(username='creatoruser', password='test')
        response = self.client.get("/piece/{0}/update/".format(piece.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        self.client.login(username='superuser', password='test')
        response = self.client.get("/piece/{0}/update/".format(piece.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_get_upload_not_allowed(self):
        response = self.client.get("/pieces/upload/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_upload_allowed(self):
        self.client.login(username='creatoruser', password='test')
        response = self.client.get("/pieces/upload/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    # Test for invalid form submission
    def test_post_create_piece_empty_form_not_allowed(self):
        self.client.login(username='testuser', password='test')
        response = self.client.post("/pieces/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.logout()

    # Test for valid form submission with all new things
    def test_post_create_piece_new_models_no_files_no_movements(self):
        self.client.login(username='testuser', password='test')
        response = self.client.post("/pieces/", {'title': 'Create Test',
                                                 'composer': 'New Composer',
                                                 'composition_start_date': 1600,
                                                 'composition_end_date': 1605,
                                                 'collections': 'New Collection',
                                                 'number_of_voices': 3,
                                                 'genres': 'New Genre',
                                                 'locations': 'New Location',
                                                 'languages': 'New Language',
                                                 'sources': 'New Source',
                                                 'instruments_voices': 'New Instrument',
                                                 'comment': "New Comment",
                                                 'religiosity': 'Secular',
                                                 'vocalization': 'Vocal',
                                                 'tags': 'New Tag'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

    # Test for finding already existing models instead of creating new ones.
    def test_post_create_piece_new_models_no_files_no_movements_check_count(self):
        self.client.login(username='testuser', password='test')
        response = self.client.post("/pieces/", {'title': 'Count Test 1',
                                                 'composer': self.test_composer,
                                                 'composition_start_date': 1600,
                                                 'composition_end_date': 1605,
                                                 'collections': 'Old Collection',
                                                 'number_of_voices': 3,
                                                 'genres': 'Old Genre',
                                                 'locations': 'Old Location',
                                                 'languages': 'Old Language',
                                                 'sources': 'Old Source',
                                                 'instruments_voices': 'Old Instrument',
                                                 'comment': "Old Comment",
                                                 'religiosity': 'Secular',
                                                 'vocalization': 'Vocal',
                                                 'tags': 'Old Tag'})

        composer_count = Composer.objects.all().count()
        collection_count = Collection.objects.all().count()
        genre_count = Genre.objects.all().count()
        location_count = Location.objects.all().count()
        language_count = Language.objects.all().count()
        source_count = Source.objects.all().count()
        instrument_count = InstrumentVoice.objects.all().count()
        tag_count = Tag.objects.all().count()

        response = self.client.post("/pieces/", {'title': 'Count Test 2',
                                                 'composer': self.test_composer,
                                                 'composition_start_date': 1600,
                                                 'composition_end_date': 1605,
                                                 'collections': 'Old Collection; New Collection',
                                                 'number_of_voices': 3,
                                                 'genres': 'Old Genre; New Genre',
                                                 'locations': 'Old Location; New Location',
                                                 'languages': 'Old Language; New Language',
                                                 'sources': 'Old Source; New Source',
                                                 'instruments_voices': 'Old Instrument; New Instrument',
                                                 'comment': "New Comment",
                                                 'religiosity': 'Secular',
                                                 'vocalization': 'Vocal',
                                                 'tags': 'Old Tag; New Tag'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(composer_count, Composer.objects.all().count())
        self.assertEqual(collection_count, Collection.objects.all().count() - 1)
        self.assertEqual(genre_count, Genre.objects.all().count() - 1)
        self.assertEqual(location_count, Location.objects.all().count() - 1)
        self.assertEqual(language_count, Language.objects.all().count() - 1)
        self.assertEqual(source_count, Source.objects.all().count() - 1)
        self.assertEqual(instrument_count, InstrumentVoice.objects.all().count() - 1)
        self.assertEqual(tag_count, Tag.objects.all().count() - 1)
        self.client.logout()

    # def test_post_create_piece_create_movement(self):
    #     self.client.login(username='testuser', password='test')
    #     movement_count = Movement.objects.all().count()
    #     response = self.client.post("/pieces/", {'title': 'Mov Create Test',
    #                                              'composer': self.test_composer,
    #                                              'composition_start_date': 1600,
    #                                              'composition_end_date': 1605,
    #                                              'collections': 'New Collection',
    #                                              'number_of_voices': 3,
    #                                              'genres': 'New Genre',
    #                                              'locations': 'New Location',
    #                                              'languages': 'New Language',
    #                                              'sources': 'New Source',
    #                                              'instruments_voices': 'New Instrument',
    #                                              'comment': "New Comment",
    #                                              'religiosity': 'Secular',
    #                                              'vocalization': 'Vocal',
    #                                              'tags': 'New Tag',
    #                                              'mov_title_1': 'Mov Create Test'})
    #     piece = Piece.objects.get(title='Mov Create Test')
    #     mov = Movement.objects.get(title='Mov Create Test')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(piece, mov.piece)
    #     self.assertEqual(piece.composer, mov.composer)
    #     self.assertEqual(piece.composition_start_date, mov.composition_start_date)
    #     self.assertEqual(piece.composition_end_date, mov.composition_end_date)
    #     self.assertEqual(list(piece.collections.all()), list(mov.collections.all()))
    #     self.assertEqual(piece.number_of_voices, mov.number_of_voices)
    #     self.assertEqual(list(piece.genres.all()), list(mov.genres.all()))
    #     self.assertEqual(list(piece.locations.all()), list(mov.locations.all()))
    #     self.assertEqual(list(piece.languages.all()), list(mov.languages.all()))
    #     self.assertEqual(list(piece.sources.all()), list(mov.sources.all()))
    #     self.assertEqual(list(piece.instruments_voices.all()), list(mov.instruments_voices.all()))
    #     self.assertEqual(piece.religiosity, mov.religiosity)
    #     self.assertEqual(piece.vocalization, mov.vocalization)
    #     self.assertEqual(list(piece.tags.all()), list(mov.tags.all()))
    #     self.client.logout()
    #
    # def test_post_create_piece_create_movement_with_overrides(self):
    #     self.client.login(username='testuser', password='test')
    #     movement_count = Movement.objects.all().count()
    #     response = self.client.post("/pieces/", {'title': 'Mov Override Test',
    #                                              'composer': self.test_composer,
    #                                              'composition_start_date': 1600,
    #                                              'composition_end_date': 1605,
    #                                              'collections': 'New Collection',
    #                                              'number_of_voices': 3,
    #                                              'genres': 'New Genre',
    #                                              'locations': 'New Location',
    #                                              'languages': 'New Language',
    #                                              'sources': 'New Source',
    #                                              'instruments_voices': 'New Instrument',
    #                                              'comment': "New Comment",
    #                                              'religiosity': 'Secular',
    #                                              'vocalization': 'Vocal',
    #                                              'tags': 'New Tag',
    #                                              'mov_title_1': 'Mov Override Test',
    #                                              'mov1_instrumentation': 'Other Instrument',
    #                                              'mov1_number_of_voices': 4,
    #                                              'mov1_free_tags': 'Other Tag',
    #                                              'mov1_vocalization': 'Mixed',
    #                                              'mov1_comment': 'Other Comment'
    #                                              })
    #     piece = Piece.objects.get(title='Mov Override Test')
    #     mov = Movement.objects.get(title='Mov Override Test')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(piece, mov.piece)
    #     self.assertEqual(piece.composer, mov.composer)
    #     self.assertEqual(piece.composition_start_date, mov.composition_start_date)
    #     self.assertEqual(piece.composition_end_date, mov.composition_end_date)
    #     self.assertEqual(list(piece.collections.all()), list(mov.collections.all()))
    #     self.assertEqual(list(piece.genres.all()), list(mov.genres.all()))
    #     self.assertEqual(list(piece.locations.all()), list(mov.locations.all()))
    #     self.assertEqual(list(piece.languages.all()), list(mov.languages.all()))
    #     self.assertEqual(list(piece.sources.all()), list(mov.sources.all()))
    #     self.assertEqual(piece.religiosity, mov.religiosity)
    #
    #     self.assertNotEqual(piece.comment, mov.comment)
    #     self.assertNotEqual(piece.vocalization, mov.vocalization)
    #     self.assertNotEqual(piece.number_of_voices, mov.number_of_voices)
    #     self.assertEqual(mov.instruments_voices.all().count(), 1)
    #     self.assertEqual(mov.instruments_voices.all()[0].name, 'Other Instrument')
    #     self.assertEqual(mov.tags.all().count(), 1)
    #     self.assertEqual(mov.tags.all()[0].name, 'Other Tag')
    #     self.client.logout()
