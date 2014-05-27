from django.conf import settings
import solr

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
        #print('parsed_request', self.parsed_request, type(self.parsed_request))
        #print('prepared_query', self.prepared_query, type(self.prepared_query))
        #print('solr_params', self.solr_params, type(self.solr_params))

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
        for k, v in qdict.lists():
            # LM: modified from just self.parsed_request[k] = v to cut out nonsensical page requests to solr
            if k == 'page':
                continue
            # LM: elif for filtration
            # check if user has ticked a filter for querying
            elif k in settings.SEARCH_FILTERS_DICT:
                # LM: Update filter_query[], the query string, accordingly
                if not filter_query:
                    filter_query += u"{0}{1}".format("type:", settings.SEARCH_FILTERS_DICT[k])
                else:
                    filter_query += u"{0}{1}".format(" OR type:", settings.SEARCH_FILTERS_DICT[k])
            # LM: Otherwise, add to query
            else:
                self.parsed_request[k] = v

        # LM: Update search parameters with the filter query --- test: u"type:elvis_piece OR type:elvis_composer"
        print(filter_query)
        self.solr_params.update({'fq': filter_query})

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
                print('arr', arr)
            self.prepared_query = u" AND ".join(arr)            
        else:
            self.prepared_query = u"*:*"