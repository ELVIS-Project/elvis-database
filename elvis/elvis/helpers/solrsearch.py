from django.conf import settings
import solr
import datetime

class SolrSearch(object):
    """ 
        This class is a helper class for translating between query parameters in a GET
        request and the format needed to search in Solr.

        It has three main methods: search, facets, and group_search.

        The search method performs a search. The `parse_request` and `prepare_query` methods
        are automatically called with the request object when the class is initialized. This
        filters all the query keys and translates them to Solr. 

        The facets method requests facets from the Solr search server.

        The group_search method performs a search, but can be used to group results on any
        given field.

        The private methods in this class (ones beginning in underscores) are helpers that
        do all the work.

    """
    def __init__(self, request):
        self.server = solr.Solr(settings.SOLR_SERVER)
        self.request = request
        self.parsed_request = {}
        self.prepared_query = u""
        self.solr_params = {}
        self._parse_request()
        self._prepare_query()
        # LM: Debugging prints
        print('parsed_request', self.parsed_request, type(self.parsed_request))
        print('prepared_query', self.prepared_query, type(self.prepared_query))
        print('solr_params', self.solr_params, type(self.solr_params))

    def search(self, **kwargs):
        self.solr_params.update(kwargs)
        res = self._do_query()
        return res

    def facets(self, facet_fields, **kwargs):
        facet_params = {
            'facet': 'true',
            'facet_field': facet_fields,
            'facet_mincount': 1
        }
        self.solr_params.update(facet_params)
        self.solr_params.update(kwargs)

        res = self._do_query()
        return res

    def group_search(self, group_fields, **kwargs):
        group_params = {
            'group': 'true',
            'group_ngroups': 'true',
            'group_field': group_fields
        }
        self.solr_params.update(group_params)
        self.solr_params.update(kwargs)

        res = self._do_query()
        return res

    def _do_query(self):
        return self.server.select(self.prepared_query, **self.solr_params)


    def _parse_request(self):
        qdict = self.request.GET
        filter_query = ""
        sort_query = ""
        date_filt_query = ""
        from_date = "" 
        to_date = ""
        for k, v in qdict.lists():

            # LM: modified from just self.parsed_request[k] = v to cut out nonsensical page requests to solr
            if k == 'page':
                continue

            # LM: elif for Type filtration
            # check if user has ticked a filter for querying
            elif k in settings.SEARCH_FILTERS_DICT:
                # LM: Update filter_query[], the query string, accordingly
                if not filter_query:
                    filter_query += u"{0}{1}".format("type:", settings.SEARCH_FILTERS_DICT[k])
                else:
                    filter_query += u"{0}{1}".format(" OR type:", settings.SEARCH_FILTERS_DICT[k])
            elif k == 'sortby':
               sort_query = qdict.get(k)

            # LM: elif for Date filtration
            elif k == 'datefiltf':
                if qdict.get('datefiltf') == "" and qdict.get('datefiltt') == "":
                    pass
                elif qdict.get('datefiltf') == "":
                    from_date = "[ * TO"
                    to_date = u"{0}-00-00T00:00:00Z ]".format(qdict.get('datefiltt'))
                elif qdict.get('datefiltt') == "":
                    from_date =  u"[ {0}-00-00T00:00:00Z TO ".format(qdict.get('datefiltf'))
                    to_date = "* ]"
                else:
                    from_date = u"[ {0}-00-00T00:00:00Z TO ".format(qdict.get('datefiltf'))
                    to_date = u"{0}-00-00T00:00:00Z ]".format(qdict.get('datefiltt'))
                date_filt_query = from_date + to_date

            # Otherwise, add to query
            elif k == 'q' :
                self.parsed_request[k] = v
            #elif k == 'format':
            #    self.parsed_request[k] = v

        self.solr_params.update({'fq': filter_query, 'sort': sort_query})

        # Update fq with date filtration, depending on what type filter was set
        if date_filt_query == "":
            pass
        elif filter_query =="":
            self.solr_params['fq'] += " date_general: " + date_filt_query
        else:
            self.solr_params['fq'] += " AND date_general: " + date_filt_query
        #elif filter_query == "" and "fcp" in qdict:
        #    self.solr_params['fq'] += " birth_date: " + date_filt_query
        #elif filter_query == "" and "fp" in qdict or "fm" in qdict:
        #    self.solr_params['fq'] += " date_of_composition: " + date_filt_query
        #elif "fcp" in qdict:
        #    self.solr_params['fq'] += " AND birth_date: " + date_filt_query
        #elif "fp" in qdict or "fm" in qdict:
        #    self.solr_params['fq'] += " AND date_of_composition: " + date_filt_query
        #else:
        #    pass


        

        # LM: Update search parameters with the filter query --- test: u"type:elvis_piece OR type:elvis_composer"
        # print(filter_query)
        

        # LM: Update search parameters with date filter 
        #self.parsed_request['q'] += u"AND ({0} OR {1})".format(composer_date_filt_query, piece_date_filt_query)



    def _prepare_query(self):
        if self.parsed_request:
            arr = []
            for k, v in self.parsed_request.iteritems():
                if not v:
                    continue
                if k == 'q':
                    if v[0] != u"":
                        arr.insert(0, u"{0}".format(v[0]))
                else:
                    arr.append(u"{0}:({1})".format(k, " OR ".join(["\"{0}\"".format(s) for s in v if v is not None])))
                # LM: Debugging print
                #print('arr', arr)
            self.prepared_query = u" AND ".join(arr)            
        else:
            self.prepared_query = u"*:*"
