# Testing imports
import unittest
#import mock
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from model_mommy import mommy

# Other tools
import datetime
import uuid
import itertools 
import os, sys

# Edda imports
from django.contrib.auth.models import AnonymousUser, User

# Solr imports
import solr
from elvis.settings import SOLR_SERVER
from elvis.helpers import paginate, solrsearch


class SolrSearchTest(TestCase):
    '''
    This test case tests the solrsearch script and the SolrSearch class
    '''
    def setUp(self):
        # Create an instance of Django's request factory
        # Create a test user instance
        self.factory = RequestFactory()
        self.test_user = mommy.make(User, username='unit_test_user')
        self.server = "fake_url"

    ##### Following are SolrSearch parsing tests #####

    def test_empty_request(self):
        # Empty query
        mock_request = self.factory.get("/search/?q=")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (not mock_solrsearch.solr_params)

    def test_page_request(self):
        # Create mock page number request
        mock_request = self.factory.get("/search/?q=&page=20")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (not mock_solrsearch.solr_params)

    def test_sort_request(self):
        # Test sorting request
        mock_request = self.factory.get("/search/?q=&sortby=name_sort+desc")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (mock_solrsearch.solr_params["sort"] == "name_sort desc")

    def test_format_filter(self):
        # Json format request is the only one handled by the search view, which has to render results accordingly
        mock_request = self.factory.get("/search/?q=&format=json")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (not mock_solrsearch.solr_params)

    def test_type_filter(self):
        # Test filtering by type
        mock_request = self.factory.get("/search/?q=&typefilt=elvis_composer&typefilt=elvis_movement&typefilt=elvis_collection")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (mock_solrsearch.solr_params["fq"] == "( type: (elvis_composer OR elvis_movement OR elvis_collection)  )")

    def test_name_filter(self):
        # Name filtration requests filters out results by a composer's name
        mock_request = self.factory.get("/search/?q=&namefilt=jacob+obrecht")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (mock_solrsearch.solr_params["fq"] == "( name_general: (jacob obrecht)  )")

    def test_title_filter(self):
        # Name filtration requests filters out results by a composer's name
        mock_request = self.factory.get("/search/?q=&titlefilt=agnus+dei")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (mock_solrsearch.solr_params["fq"] == "( title_searchable: (agnus dei)  )")

    def test_date_filter1(self):
        from_date = "1500"
        to_date = " * "
        mock_request = self.factory.get("/search/?q=&datefiltf=" + from_date)
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        from_date = " " + from_date + "-00-00T00:00:00Z "
        assert (mock_solrsearch.parsed_request["q"] == "* AND ( (date_general: [{0} TO {1}] AND date_general2: [{2} TO {3}])^2 OR (date_general: [ * TO {4}] AND date_general2:[{5} TO * ]) )".format(from_date, to_date, from_date, to_date, to_date, from_date))
        #assert (mock_solrsearch.prepared_query == "*")

    def test_date_filter2(self):
        from_date = " * "
        to_date = "1550"
        mock_request = self.factory.get("/search/?q=&datefiltt=" + to_date)
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        to_date = " " + to_date + "-12-31T23:59:59Z "
        assert (mock_solrsearch.parsed_request["q"] == "* AND ( (date_general: [{0} TO {1}] AND date_general2: [{2} TO {3}])^2 OR (date_general: [ * TO {4}] AND date_general2:[{5} TO * ]) )".format(from_date, to_date, from_date, to_date, to_date, from_date))
        #assert (mock_solrsearch.prepared_query == "*")

    def test_date_filter3(self):
        from_date = "1500"
        to_date = "1550"
        mock_request = self.factory.get("/search/?q=&datefiltf=" + from_date + "&datefiltt=" + to_date)
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        from_date = " " + from_date + "-00-00T00:00:00Z "
        to_date = " " + to_date + "-12-31T23:59:59Z "
        assert (mock_solrsearch.parsed_request["q"] == "* AND ( (date_general: [{0} TO {1}] AND date_general2: [{2} TO {3}])^2 OR (date_general: [ * TO {4}] AND date_general2:[{5} TO * ]) )".format(from_date, to_date, from_date, to_date, to_date, from_date))
        #assert (mock_solrsearch.prepared_query == "*")

    def test_tag_filter(self):
        mock_request = self.factory.get("/search/?q=&tagfilt=mass+parody+OR+(latin+AND+sacred)+")
        mock_solrsearch = solrsearch.SolrSearch(mock_request, self.server)
        assert (mock_solrsearch.parsed_request["q"] == "*")
        assert (mock_solrsearch.prepared_query == "*")
        assert (mock_solrsearch.solr_params["fq"] == "( tags_searchable: (mass parody OR (latin AND sacred) )  )")

    



