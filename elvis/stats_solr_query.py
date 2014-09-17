from django.conf import settings
import django
import os
import json
import collections
import itertools

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")
django.setup()

from django.contrib.auth.models import User
from django.test.client import RequestFactory
from elvis.helpers.solrsearch import SolrSearch


##### All queries are contingent on how the database and metadata are organised at runtime #####

class StatisticsQuery():

    def __init__(self, start_date=1200, end_date=2050, increments=50, types=["elvis_piece", "elvis_movement"], tags=["mass", "sacred", "parody", "SATB"]):
        # Required properties
        self.__factory = RequestFactory()
        self.__QUERIES = []
        self.__QUERY_RESULTS = {}
        self.__STAT_DICT = {}

        # User-assigned properties
        self.__START_DATE = start_date
        self.__END_DATE = end_date
        self.__DATE_INCR = increments
        self.__TYPES = types
        self.__TAGS = tags
        self.__TAG_COMBOS = []
        for i in range(1, len(tags)+1):
            self.__TAG_COMBOS.extend(itertools.combinations(tags, i))
        
    def run_date_stats(self, strict_dates=""):
        result_dict = {}
        stat_dict = {}
        # Date statistics for pieces only
        for date in range(self.__START_DATE, self.__END_DATE, self.__DATE_INCR):
            for this_type in self.__TYPES:
                query = "?q=&datefiltf={0}&datefiltt={1}&type={2}{3}".format(date, date+50, this_type, strict_dates)
                self.__QUERIES.append(query)
                results = self.do_query(query)
                result_dict[query] = results.results                
                stat_dict["{0}-{1}, type: {2}".format(date, date+50, this_type)] = int(results.numFound)
        return stat_dict

    def run_tag_stats(self, flat=False):
        result_dict = {}
        stat_dict = {}
        if flat:
            for tag in self.__TAGS:
                for this_type in self.__TYPES:
                    query = "?q=&tags={0}&type={1}".format(tag, this_type)
                    self.__QUERIES.append(query)
                    results = self.do_query(query)
                    result_dict[query] = results.results                
                    stat_dict["tags: {0}, type: {1}".format(tag, this_type)] = int(results.numFound)
        else:    
            for tag_combo in self.__TAG_COMBOS:
                tag_query_string = ""
                for tag in tag_combo:
                    tag_query_string += "&tags={0}".format(tag)
                for this_type in self.__TYPES:
                    query = "?q={0}&type={1}".format(tag_query_string, this_type)
                    self.__QUERIES.append(query)
                    results = self.do_query(query)
                    result_dict[query] = results.results                
                    stat_dict["tags: {0}, type: {1}".format(tag_combo, this_type)] = int(results.numFound)
        return stat_dict

    def do_query(self, query):
        # Make a dummy get request (because we're requerying without pagination)
        dummy_request = self.__factory.get(query)
        s = SolrSearch(dummy_request)
        search_results = s.search()
        return search_results

    def print_stats(self):

        #### Query date stats -- loose
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_date_stats().items()))
        piece_total = 0
        mvt_total = 0
        print ("===== Querying date statistics =====")
        print ("--- Loose query; there may duplicates in results.")
        for query, stat in self.__STAT_DICT.iteritems():
            print (query + ": " + str(stat))
            if "elvis_piece" in query:
                piece_total += stat
            elif "elvis_movement" in query:
                mvt_total += stat
        print "Total pieces: " + str(piece_total)
        print "Total movements: " + str(mvt_total)
        print ""

        #### Query date stats -- strict
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_date_stats(strict_dates="&strictdates=true").items()))
        piece_total = 0
        mvt_total = 0
        print ("--- Strict query; not all pieces may be returned, depending on size of searched date-range.")
        for query, stat in self.__STAT_DICT.iteritems():
            print (query + ": " + str(stat))
            if "elvis_piece" in query:
                piece_total += stat
            elif "elvis_movement" in query:
                mvt_total += stat
        print "Total pieces: " + str(piece_total)
        print "Total movements: " + str(mvt_total)
        print ""
        
        #### Query tag stats 
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_tag_stats(flat=True).items()))
        piece_total = 0
        mvt_total = 0
        print ("===== Querying tag statistics =====")
        print ("--- Flat query ---")
        for query, stat in self.__STAT_DICT.iteritems():
            print (query + ": " + str(stat))
            if "elvis_piece" in query:
                piece_total += stat
            elif "elvis_movement" in query:
                mvt_total += stat
        print "Total pieces: " + str(piece_total)
        print "Total movements: " + str(mvt_total)
        print ""

        #### Query tag stats 
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_tag_stats().items()))
        piece_total = 0
        mvt_total = 0
        print ("--- Combined query ---")
        for query, stat in self.__STAT_DICT.iteritems():
            print (query + ": " + str(stat))
            if "elvis_piece" in query:
                piece_total += stat
            elif "elvis_movement" in query:
                mvt_total += stat
        print "Total pieces: " + str(piece_total)
        print "Total movements: " + str(mvt_total)
        print ""

s = StatisticsQuery()
s.print_stats()
