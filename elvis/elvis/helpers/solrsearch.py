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
            'facet_limit': 1000,
            'facet_mincount': 1,
            'facet_sort' : 'count',
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

            # LM: elif for Type filtration
            # check if user has ticked a filter for querying
            #elif k in settings.SEARCH_FILTERS_DICT:
                # LM: Update filter_query[], the query string, accordingly
            #    if not filter_query:
            #        filter_query += u"{0}{1}".format("type:", settings.SEARCH_FILTERS_DICT[k])
            #    else:
            #        filter_query += u"{0}{1}".format(" OR type:", settings.SEARCH_FILTERS_DICT[k])

            # LM: Elif for Type filtration
            elif k == 'typefilt':
                filter_query = "type: ("  + string.join((v), ' OR ') + ") "

            # LM: elif for sorting
            elif k == 'sortby':
               sort_query = qdict.get(k)

            # LM: elif for Name filtration
            elif k == 'namefilt':
                name_filt_query = "name_general: (" + string.join(v) +") "

            elif k == 'titlefilt':
                title_filt_query = "title_searchable: (" + string.join(v) +") "

            # LM: elif for Date filtration
            elif k == 'datefiltf' or k == 'datefiltt':
                if qdict.get('datefiltf') == "" or qdict.get('datefiltf') is None:
                    from_date = " date_general: [ * TO "
                    to_date = u"{0}-12-31T23:59:59Z ]".format(qdict.get('datefiltt'))
                elif qdict.get('datefiltt') == "" or qdict.get('datefiltt') is None:
                    from_date =  u" date_general: [ {0}-00-00T00:00:00Z TO ".format(qdict.get('datefiltf'))
                    to_date = "* ]"
                else:
                    from_date = u" date_general: [ {0}-00-00T00:00:00Z TO ".format(qdict.get('datefiltf'))
                    to_date = u"{0}-12-31T23:59:59Z ]".format(qdict.get('datefiltt'))
                date_filt_query = from_date + to_date

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
                    v = "*"
                self.parsed_request[k] = v
            
            else:
                self.parsed_request[k] = v
        
        self.solr_params.update({'sort': sort_query})


        if filter_query != "":
            self.solr_params['fq'] = "( " + filter_query + " )"

        if date_filt_query == "":
            pass
        elif not 'fq' in self.solr_params:
            self.solr_params['fq'] = "( " + date_filt_query + " )"
        else:
            self.solr_params['fq'] += " AND ( " + date_filt_query + " )"

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



        # Update fq with date filtration, depending on what type filter was set
        #if date_filt_query == "":
        #    pass            
        #elif filter_query =="":
        #    self.solr_params['fq'] += date_filt_query
        #else:
        #    self.solr_params['fq'] = "( " + filter_query + " )" + " AND " + date_filt_query
            # u"( {0} ) AND date_general: {1}".format(filter_query, date_filt_query) 
            #print self.solr_params['fq']
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
                    # was OR by default
                    arr.append(u"{0}:({1})".format(k, " AND ".join([u"\"{0}\"".format(s) for s in v if v is not None])))
                # LM: Debugging print
                #print('arr', arr)
            self.prepared_query = u" AND ".join(arr)            
        else:
            self.prepared_query = u"*:*"
