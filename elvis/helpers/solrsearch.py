from django.conf import settings
import solr
import datetime
import string

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
    def __init__(self, request, server=settings.SOLR_SERVER):
        self.server = solr.Solr(server)
        self.request = request
        self.parsed_request = {}
        self.prepared_query = u""
        self.solr_params = {}
        self._parse_request()
        self._prepare_query()

    def search(self, **kwargs):
        self.solr_params.update(kwargs)
        res = self._do_query()
        return res

    def facets(self, facet_fields, **kwargs):
        facet_params = {
            'facet': 'true',
            'facet_field': facet_fields,
            'facet_limit': 1000,
            'facet_mincount': 1,
            'facet_sort': 'count',
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
        tag_filt_query = ""
        date_filt_query = ""
        name_filt_query = ""
        title_filt_query = ""
        voice_filt_query = ""
        from_date = "" 
        to_date = ""
        #print qdict.lists()
        for k, v in qdict.lists():

            # LM: modified from just self.parsed_request[k] = v to cut out nonsensical page/format requests to solr
            if k == 'page' or k == 'format':
                continue
            # LM: Elif for Type filtration
            elif k == 'typefilt':
                filter_query = "type: ("  + string.join(v, ' OR ') + ") "

            # LM: elif for sorting
            elif k == 'sortby':
               sort_query = qdict.get(k)

            # LM: elif for Name filtration
            elif k == 'namefilt':
                name_filt_query = "name_general: (" + string.join(v) +") "

            elif k == 'titlefilt':
                title_filt_query = "title_searchable: (" + string.join(v) +") "

            # LM: elif for Date filtration
            # Logic: We want start date to be any time before 2nd search date, and end date to be any time after 1st search date
            # However, we want things that have start and end dates between the two search dates to be ordered first -- thus the 
            # ^2 weighting.
            elif k == 'datefiltf' or k == 'datefiltt' or k == 'strictdates':
                if qdict.get('datefiltf') is None or qdict.get('datefiltf').replace(" ", "") in ["", "*"]:
                    from_date = " * "
                else:
                    from_date = u" {0}-00-00T00:00:00Z ".format(qdict.get('datefiltf'))
                if qdict.get('datefiltt') is None or qdict.get('datefiltt').replace(" ", "") in ["", "*"]:
                    to_date = " * "
                else:
                    to_date = u" {0}-12-31T23:59:59Z ".format(qdict.get('datefiltt'))
                if not qdict.get('strictdates') is None:
                    date_filt_query = "(date_general: [{0} TO {1}] AND date_general2: [{2} TO {3}])".format(from_date, to_date, from_date, to_date)
                else:
                    date_filt_query = "(date_general: [{0} TO {1}] AND date_general2: [{2} TO {3}])^2 OR (date_general: [ * TO {4}] AND date_general2:[{5} TO * ])".format(from_date, to_date, from_date, to_date, to_date, from_date)

            # LM: elif for Tag filtration
            elif k == 'tagfilt':
                tag_filt_query = "tags_searchable: (" + string.join(v) + ") "


            # LM: elif for Voice filtration
            elif k == 'voicefilt':
                voice_filt_query = "number_of_voices: (" + string.join(v) + ") "

                
            elif k == 'rows':
                self.solr_params.update({'rows': v})  

            # Otherwise, add to query
            elif k == 'q' :
                if qdict.get(k) == "":
                    v = "*:*"
                self.parsed_request[k] = "( " + v[0] + " )"
            
            else:
                self.parsed_request[k] = v
        
        if sort_query:
            self.solr_params.update({'sort': sort_query})

        # Use filtered queries for advanced searches
        if filter_query != "":
            self.solr_params['fq'] = "( " + filter_query + " )"

        if tag_filt_query == "":
            pass
        elif not 'fq' in self.solr_params:
            self.solr_params['fq'] = "( " + tag_filt_query + " )"
        else:
            self.solr_params['fq'] += " AND ( " + tag_filt_query + " )"

        if name_filt_query == "":
            pass
        elif not 'fq' in self.solr_params:
            self.solr_params['fq'] = "( " + name_filt_query + " )"
        else:
            self.solr_params['fq'] += " AND (" + name_filt_query + " )"

        if title_filt_query == "":
            pass
        elif not 'fq' in self.solr_params:
            self.solr_params['fq'] = "( " + title_filt_query + " )"
        else:
            self.solr_params['fq'] += " AND (" + title_filt_query + " )"

        if voice_filt_query == "":
            pass
        elif not 'fq' in self.solr_params:
            self.solr_params['fq'] = "( " + voice_filt_query + " )"
        else:
            self.solr_params['fq'] += " AND (" + voice_filt_query + " )"

        # ... with the exception of dates, for which the default select solr method is used to preserve ranking by date
        if date_filt_query == "":
            pass
        elif not 'q' in self.parsed_request:
            self.parsed_request['q'] = "( " + date_filt_query + " )"
        else:
            self.parsed_request['q'] += " AND ( " + date_filt_query + " )"


    def _prepare_query(self):
        if self.parsed_request:
            arr = []
            for k, v in self.parsed_request.iteritems():
                if not v:
                    continue
                if k == 'q':
                    if v[0] != u"":
                        arr.insert(0, u"{0}".format(v))
                else:
                    # was OR by default
                    arr.append(u"{0}:({1})".format(k, " AND ".join([u"\"{0}\"".format(s) for s in v if v is not None])))
            self.prepared_query = u" AND ".join(arr)            
        else:
            self.prepared_query = u"*:*"
