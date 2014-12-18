from django.conf import settings
import django
import os
import json
import collections
import itertools
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elvis.settings")
django.setup()

from django.contrib.auth.models import User
from django.test.client import RequestFactory
from elvis.helpers.solrsearch import SolrSearch


##### All queries are contingent on how the database and metadata are organised at runtime #####

class StatisticsQuery():

    def __init__(self, start_date=1200, end_date=2050, increments=50, types=["elvis_piece", "elvis_movement"], tags=["mass", "symphony", "string quartet", "motet", "chanson"]):
        # Required properties
        self.__factory = RequestFactory()
        self.__QUERIES = []
        self.__QUERY_RESULTS = {}
        self.__STAT_DICT = {}
        self.__STAT_MATRIX = []
        self.__CSV_PATH = "elvis_db_stats.csv"

        # User-assigned properties
        self.__START_DATE = start_date
        self.__END_DATE = end_date
        self.__DATE_INCR = increments
        self.__TYPES = types
        self.__TAGS = tags
        self.__TAG_COMBOS = []
        self.__VOICE_NUMS = range(0, 25)

        # Generate all combinations of tags
        for i in range(1, len(tags)+1):
            self.__TAG_COMBOS.extend(itertools.combinations(tags, i))

    def run_blank_stats(self):
        result_dict = {}
        stat_dict = {}
        self.__STAT_MATRIX.append(["Blank Statistics"])
        for this_type in self.__TYPES:
            query = "?q=&type={0}".format(this_type)
            self.__QUERIES.append(query)
            results = self.do_query(query)
            result_dict[query] = results.results                
            stat_dict["type: {0}".format(this_type)] = int(results.numFound)
            self.__STAT_MATRIX.append([this_type, "blank", int(results.numFound)])
        return stat_dict
        
    def run_date_stats(self, strict_dates=""):
        result_dict = {}
        stat_dict = {}
        self.__STAT_MATRIX.append(["Date Statistics (" + strict_dates + ")"])
        # Date statistics
        for this_type in self.__TYPES:
            for date in range(self.__START_DATE, self.__END_DATE, self.__DATE_INCR):
                query = "?q=&datefiltf={0}&datefiltt={1}&type={2}{3}".format(date, date+50, this_type, strict_dates)
                self.__QUERIES.append(query)
                results = self.do_query(query)
                result_dict[query] = results.results                
                stat_dict["type: {0}, {1}-{2}".format(this_type, date, date+50)] = int(results.numFound)
                self.__STAT_MATRIX.append([this_type, date, int(results.numFound)])
        return stat_dict

    def run_voicenum_stats(self):
        result_dict = {}
        stat_dict = {}
        self.__STAT_MATRIX.append(["Voice Number Statistics"])
        # Date statistics
        for this_type in self.__TYPES:
            for voicenum in self.__VOICE_NUMS:
                query = "?q=&number_of_voices={0}&type={1}".format(voicenum, this_type)
                self.__QUERIES.append(query)
                results = self.do_query(query)
                result_dict[query] = results.results                
                stat_dict["type: {0}, voice_number: {1}".format(this_type, voicenum)] = int(results.numFound)
                self.__STAT_MATRIX.append([this_type, voicenum, int(results.numFound)])
        return stat_dict

    def run_tag_stats(self, flat=False):
        result_dict = {}
        stat_dict = {}
        stat_matrix = []
        if flat:
            self.__STAT_MATRIX.append(["Flat Tag Statistics"])
            for this_type in self.__TYPES:
                for tag in self.__TAGS:    
                    query = "?q=&tags={0}&type={1}".format(tag, this_type)
                    self.__QUERIES.append(query)
                    results = self.do_query(query)
                    result_dict[query] = results.results                
                    stat_dict["type: {0}, tags: {1}".format(this_type, tag)] = int(results.numFound)
                    self.__STAT_MATRIX.append([this_type, tag, int(results.numFound)])
        else:
            self.__STAT_MATRIX.append(["Combined Tag Statistics"])
            for this_type in self.__TYPES:    
                for tag_combo in self.__TAG_COMBOS:
                    tag_query_string = ""
                    for tag in tag_combo:
                        tag_query_string += "&tags={0}".format(tag)
                    query = "?q={0}&type={1}".format(tag_query_string, this_type)
                    self.__QUERIES.append(query)
                    results = self.do_query(query)
                    result_dict[query] = results.results                
                    stat_dict["type: {0}, tags: {1}".format(this_type, tag_combo)] = int(results.numFound)
                    self.__STAT_MATRIX.append([this_type, tag_combo, int(results.numFound)])
        return stat_dict

    def do_query(self, query):
        dummy_request = self.__factory.get(query)
        s = SolrSearch(dummy_request)
        search_results = s.search()
        return search_results

    def __iteration_print(self):
        piece_total = 0
        mvt_total = 0
        for query, stat in self.__STAT_DICT.iteritems():
            print (query + ": " + str(stat))
            if "elvis_piece" in query:
                piece_total += stat
            elif "elvis_movement" in query:
                mvt_total += stat
        print "Total pieces: " + str(piece_total)
        print "Total movements: " + str(mvt_total)
        print ""

    def __write_to_csv(self):
        # Use fresh stats
        if os.path.isfile(self.__CSV_PATH):
            os.remove(self.__CSV_PATH)
        with open(self.__CSV_PATH, 'wb') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel')
            csv_writer.writerow(['Type', 'Query', 'Frequency'])
            for row in self.__STAT_MATRIX:
                csv_writer.writerow(row)

    def do_stats(self):
        #### Blank search stats
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_blank_stats().items()))
        print ("===== Querying blank statistics =====")
        self.__iteration_print()

        #### Query date stats -- loose
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_date_stats().items()))
        print ("===== Querying date statistics =====")
        print ("--- Loose query; there may duplicates in results.")
        self.__iteration_print()

        #### Query date stats -- strict
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_date_stats(strict_dates="&strictdates=true").items()))
        print ("--- Strict query; not all pieces may be returned, depending on size of searched date-range.")
        self.__iteration_print()

        #### Query date stats -- loose
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_voicenum_stats().items()))
        print ("===== Querying voice-number statistics =====")
        self.__iteration_print()
        
        #### Query tag stats 
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_tag_stats(flat=True).items()))
        print ("===== Querying tag statistics =====")
        print ("--- Flat query ---")
        self.__iteration_print()

        #### Query tag stats 
        self.__STAT_DICT = collections.OrderedDict(sorted(self.run_tag_stats().items()))
        print ("--- Combined query ---")
        self.__iteration_print()

        self.__write_to_csv()

s = StatisticsQuery()
s.do_stats()
