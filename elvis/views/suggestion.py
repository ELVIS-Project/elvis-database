import pdb
from django.http import HttpResponse
from django.conf import settings
import json
import urllib2
import solr


def suggest(request):
    results = []

    if request.method == "GET" and request.GET.has_key(u'q') and request.GET.has_key(u'd'):
        value = request.GET[u'q']
        dictionary = request.GET[u'd']
        if len(value) > 1:
                URLVal = value.replace(" ", "+")
                json_string = urllib2.urlopen(settings.SOLR_SERVER + "/suggest/?wt=json&suggest.dictionary={0}&q={1}".format(dictionary, URLVal))
                data = json.loads(json_string.read())['suggest']['{0}'.format(dictionary)]['{0}'.format(value)]

                if data['numFound'] > 0:
                    for suggestion in data['suggestions']:
                        results.append({'name': suggestion['term']})
    j_results = json.dumps(results)
    return HttpResponse(j_results, content_type="json")