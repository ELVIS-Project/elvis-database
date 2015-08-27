from django.conf import settings
import re
import solr
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
        filter_query = []
        general_query = []

        for k in list(qdict.keys()):
            # Filter Parameters
            if k == 'titlefilt':
                title_filt = "title_searchable:({0})".format(self.parse_bool(qdict[k]))
                self.solr_params['fq'].append(title_filt)
                continue

            if k =='namefilt':
                name_filt = "name_general:({0})".format(self.parse_bool(qdict[k]))
                self.solr_params['fq'].append(name_filt)
                continue

            if k =='voicefilt':
                voice_filt = "number_of_voices:({0})".format(self.parse_bool(qdict[k]))
                self.solr_params['fq'].append(voice_filt)
                continue

            if k =='tagfilt':
                tag_filt = "tags:({0})".format(self.parse_bool(qdict['tagfilt']))
                self.solr_params['fq'].append(tag_filt)
                continue

            if k =='genrefilt':
                genre_filt = "genres:({0})".format(self.parse_bool(qdict['genrefilt']))
                self.solr_params['fq'].append(genre_filt)
                continue

            if k =='instrumentfilt':
                ins_filt = "instruments_voices:({0})".format(self.parse_bool(qdict['instrumentfilt']))
                self.solr_params['fq'].append(ins_filt)
                continue

            if k =='languagefilt':
                lan_filt = "languages:({0})".format(self.parse_bool(qdict['languagefilt']))
                self.solr_params['fq'].append(lan_filt)
                continue

            if k =='sourcesfilt':
                source_filt = "sources:({0})".format(self.parse_bool(qdict['sourcesfilt']))
                self.solr_params['fq'].append(source_filt)
                continue

            if k =='locationsfilt':
                loc_filt = "locations:({0})".format(self.parse_bool(qdict['locationsfilt']))
                self.solr_params['fq'].append(loc_filt)
                continue

            if k =='typefilt[]':
                type_filt = "type:"
                type_filt += ' OR '.join(qdict.getlist('typefilt[]'))
                self.solr_params['fq'].append(type_filt)
                continue

            if k =='filefilt[]':
                file_filt = "file_formats:"
                file_filt += ' OR '.join(qdict.getlist('filefilt[]'))
                self.solr_params['fq'].append(file_filt)
                continue

            if k =='vocalizationfilt':
                voc_filt = "vocalization:"
                voc_filt += ' OR '.join(qdict.getlist('vocalizationfilt'))
                self.solr_params['fq'].append(voc_filt)
                continue

            if k =='religiosityfilt':
                rel_filt = "religiosity:"
                rel_filt += ' OR '.join(qdict.getlist('religiosityfilt'))
                self.solr_params['fq'].append(rel_filt)
                continue

            if k == 'datefiltf':
                from_date = " {0}-00-00T00:00:00Z ".format(str(int(qdict.get('datefiltf')) + 1))
                if qdict.get('datefiltt'):
                    to_date = " {0}-00-00T00:00:00Z ".format(str(int(qdict.get('datefiltt')) + 1))
                    date_filt = "(date_general:[{0} TO {1}] OR date_general2:[{0} TO {1}])".format(from_date, to_date)
                else:
                    date_filt = "(date_general:[{0} TO *] OR date_general2:[{0} TO *])".format(from_date)
                self.solr_params['fq'].append(date_filt)
                continue
            elif k == 'datefiltt':
                to_date = " {0}-00-00T00:00:00Z ".format(str(int(qdict.get('datefiltt')) + 1))
                date_filt = "(date_general:[* TO {0}] OR date_general2:[* TO {0}])".format(to_date)
                self.solr_params['fq'].append(date_filt)
                continue

            # Query Parameters
            if k == 'composer_name':
                general_query.append('(composer_name:"{0}")'.format(qdict[k]))
                continue
            if k == 'type':
                general_query.append('(type:"{0}")'.format(qdict[k]))
                continue
            if k == 'number_of_voices':
                general_query.append('(number_of_voices:{0})'.format(qdict[k]))
                continue
            if k == 'tags':
                tag_query = '(tags:"{0}")'.format(qdict[k])
                general_query.append(tag_query)
                continue
            if k == 'tags[]':
                tags = str(qdict.getlist('tags[]'))
                tags = '" AND "'.join(x for x in tags)
                tag_query = '(tags:"{0}")'.format(tags)
                general_query.append(tag_query)
                continue

            # Sorting
            if k == 'sortby':
                self.solr_params.update({'sort': qdict.get(k)})

            if k =='rows':
                self.solr_params.update({'rows': qdict.get(k)})

        if qdict.get('q'):
            keywords = "({0})".format(self.parse_bool(qdict['q'], general=True))
            general_query.append(keywords)
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
                return bool_string
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