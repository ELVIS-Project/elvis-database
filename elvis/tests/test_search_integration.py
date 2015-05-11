# Core imports
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from model_mommy import mommy
import datetime
import uuid
import itertools 
import os, sys

# EDDA imports
from elvis.models.tag import Tag
from elvis.models.composer import Composer
from django.contrib.auth.models import User
from elvis.models.collection import Collection
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from django.contrib.auth.models import User

# Solr imports
import solr
from elvis.settings import SOLR_SERVER


class SearchIndependentTest(TestCase):
    '''
    This is a test case that tests whether content may be added to the DB and searched for, with 
    the consideration that they will be added and removed from Solr automatically
    '''
    def setUp(self):
        # Create a series of names for composers, collections, tags
        # TODO: autogenerate (1) unique names, (2) names with (1) as substrings, (3) combination of those names as vectors
        # FURTHER TODO: add the new fields for testing... when the switch happens

        self.COMPOSER_NAMES = []#["Quine, W.V.O", "Kripke, Saul", "Putnam, Hilary"]
        
        self.COLLECTION_NAMES = []#["Oxford University Press", "British Journal of Philosophy", "Erkenntnis"]

        self.DISJOINT_TAG_NAMES = []#["Epistemic", "Counterfactual", "Analytic Truth"]
        # Overlapping tag names are tag names in which there are significant substrings from other tag names... can generally keep this empty
        self.OVERLAPPING_TAG_NAMES = []#["Epistemic Contextualism", "Counterfactual Modal Logic", "Analytic Synthetic Truth Distinction"]
        self.TAG_NAMES = self.DISJOINT_TAG_NAMES.extend(self.OVERLAPPING_TAG_NAMES)

        # Use this to generate the m2m tag fields for pieces and movements... will in the future have to also test collections
        self.TAG_COMBO_NAMES = []
        if not self.TAG_NAMES is None:
            for i in range(1, len(self.TAG_NAMES)+1):
                self.TAG_COMBO_NAMES.extend(itertools.combinations(self.TAG_NAMES, i))

        # Date pairs are, in this case, composition date pairs... TODO generate composers with these dates, perhaps by zipping this 
        # COMPOSER_NAMES
        self.DATE_PAIRS = []

        # Create a test client
        #self.client = Client()
        # Connect to solr, for query testing independent of Django
        self.solrconn = solr.SolrConnection(SOLR_SERVER) 

        # Instantiate composers, collections, tags using model_mommy
        #self.test_user = mommy.make(User)
        #self.composers = [mommy.make(Composer, name=this_name) for this_name in self.COMPOSER_NAMES]
        #self.tags = [mommy.make(Tag, name=this_name) for this_name in self.TAG_NAMES]
        #self.collections = [mommy.make(Collection, name=this_name) for this_name in self.COLLECTION_NAMES]

    #### Initial tests

    def test_django_content_exists(self):
        # Verify that content has been added to DB without errors
        pass
        #assert User.objects.count() != 0
        #assert Composer.objects.count() == len(self.composers)
        #assert Tag.objects.count() == len(self.tags)
        #assert Collection.objects.count() == len(self.collections)

    def test_solr_content_exists(self):
        # Verify that content has been added to solr

        pass

    #### Basic search tests

    def test_search_composers(self):
        # Verify that composers are searchable through django
        pass

    def test_search_collections(self):
        # Verify that collections are searchable through django
        pass

    def test_search_tags(self):
        # Verify that tags are searchable through django
        pass

    #### General "textual content" test

    def test_general_search(self):
        # Select a couple of keywords by which to search
        pass

    def test_general_search_rank(self):
        # Verify that the general search returns correctly ranked items
        pass

    #### Search by date test

    def test_search_by_dates(self):
        # Verify that composers, mvts, pieces are searchable through dates
        # Only want a loose search for now, I guess
        pass

    def test_search_by_dates_rank(self):
        # Verify that searching using a date-range returns entries in the right ranking
        pass

    #### Search via composer

    def test_search_by_composers(self):
        # Self explanatory
        pass



    
