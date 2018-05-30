from django.conf import settings
import re
import solr

SOLR_FILTER_MAP = {
    'titlefilt': 'title_searchable',
    'namefilt': 'name_general',
    'voicefilt': 'number_of_voices',
    'tagfilt': 'tags',
    'genrefilt': 'genres',
    'instrumentfilt': 'instruments_voices',
    'languagefilt': 'languages',
    'sourcesfilt': 'sources',
    'locationsfilt': 'locations',
    'typefilt[]': 'type',
    'typefilt': 'type',
    'filefilt[]': 'file_formats',
    'filefilt': 'file_formats',
    'vocalizationfilt': 'vocalization',
    'religiosityfilt': 'religiosity',
}

class SolrSearch(object):
    """
        This class is a helper class for translating between query parameters in a GET
        request and the format needed to search in Solr.

        It has three main methods: search, facets, and group_search.

        The search method performs a search. The `parse_request` method
        is automatically called with the request object when the class is initialized. This
        filters all the query keys and translates them to Solr.

        The facets method requests facets from the Solr search server.

        The group_search method performs a search, but can be used to group results on any
        given field.

        The private methods in this class (ones beginning in underscores) are helpers that
        do all the work.

    """
    def __init__(self, request, server=settings.SOLR_SERVER):
        self.request = request
        self.server = solr.SolrConnection(server)
        self.parsed_request = {}
        self.prepared_query = ""
        self.solr_params = {'wt': 'json', 'fq':[]}
        self._parse_request()

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
        general_query = []

        for k in list(qdict.keys()):
            # it would be way more efficient to try calling the keys individually
            # rather than iterating over them.
            # Filter Parameters
            mapped_filter = SOLR_FILTER_MAP.get(k)
            if mapped_filter:
                filter_string = "{}:({})".format(mapped_filter, ' OR '.join(qdict.getlist(k)))
                self.solr_params['fq'].append(filter_string)

            elif k == 'datefiltf':
                from_date = " {0}-01-01T00:00:00Z ".format(str(int(qdict.get('datefiltf')) + 1))
                if qdict.get('datefiltt'):
                    to_date = " {0}-01-01T00:00:00Z ".format(str(int(qdict.get('datefiltt')) + 1))
                    date_filt = "(date_general:[{0} TO {1}] OR date_general2:[{0} TO {1}])".format(from_date, to_date)
                else:
                    date_filt = "(date_general:[{0} TO *] OR date_general2:[{0} TO *])".format(from_date)
                self.solr_params['fq'].append(date_filt)
            elif k == 'datefiltt':
                to_date = " {0}-01-01T00:00:00Z ".format(str(int(qdict.get('datefiltt')) + 1))
                date_filt = "(date_general:[* TO {0}] OR date_general2:[* TO {0}])".format(to_date)
                self.solr_params['fq'].append(date_filt)

            # Query Parameters
            elif k == 'composer_name':
                general_query.append('(composer_name:"{0}")'.format(qdict[k]))
            elif k == 'type':
                general_query.append('(type:"{0}")'.format(qdict[k]))
            elif k == 'number_of_voices':
                general_query.append('(number_of_voices:{0})'.format(qdict[k]))
            elif k == 'tags':
                tag_query = 'tags:("{0}")'.format(qdict[k])
                general_query.append(tag_query)
            elif k == 'tags[]':
                tags = qdict.getlist('tags[]')
                tags = '" AND "'.join(tags)
                tag_query = 'tags:("{0}")'.format(tags)
                general_query.append(tag_query)

            # Sorting
            elif k == 'sortby':
                self.solr_params.update({'sort': qdict.get(k)})

            elif k =='rows':
                self.solr_params.update({'rows': qdict.get(k)})

        if qdict.get('q'):
            args = self.parse_bool(qdict['q'], general=True)
            if type(args) == str:
                key_query = args
            else:
                keywords = '" AND "'.join(x for x in args)
                key_query = '"{0}"'.format(keywords)
            general_query.append(key_query)
        else:
            general_query.append("(*:*)")
        if not qdict.get('typefilt[]') and not qdict.get('type'):
            self.solr_params['fq'].append("type:(elvis_piece OR elvis_movement OR elvis_collection OR elvis_composer)")

        # AND together the query.
        self.prepared_query = " AND ".join(general_query)

    def parse_bool(self, bool_string, **kwargs):
        bools = ['AND', 'OR', 'NOT']
        if not any(x in bool_string for x in bools):
            if kwargs.get('general'):
                return bool_string.split()
            else:
                return '"{0}"'.format(bool_string)

        if bool_string.startswith('NOT'):
            bool_string = "* AND " + bool_string

        bools = ['AND', 'OR', 'NOT', '(', ')']
        args = re.split('(AND|OR|NOT|[(]|[)])', bool_string)
        formatted_bool = []
        for a in args:
            a = a.strip()
            if not a or a == "":
                continue
            if a not in bools and a != '*':
                formatted_bool.append('"{0}"'.format(a))
            else:
                formatted_bool.append('{0}'.format(a))
        return " ".join(x for x in formatted_bool)
