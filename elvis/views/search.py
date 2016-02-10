from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from django.conf import settings

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.helpers.solrsearch import SolrSearch
from elvis.helpers import paginate
from elvis.views.download import add_item


class SearchViewHTMLRenderer(CustomHTMLRenderer):
    template_name = "search/search.html"


def parse_facets(facets):
    """
    Parse search facet parameters.
    :param facets:
    :return:
    """
    facet_fields = facets.facet_counts['facet_fields']
    facet_type = {t:s for (t,s) in facet_fields['type'].items()}
    facet_composer_name = {t:s for (t,s) in facet_fields['composer_name'].items()}
    facet_tags = {t:s for (t,s) in facet_fields['tags'].items()}
    facet_number_of_voices = {t:s for (t,s) in facet_fields['number_of_voices'].items()}
    facet_parent_collection_names = {t:s for (t,s) in facet_fields['parent_collection_names'].items()}
    return {
        'type': facet_type,
        'composer_name': facet_composer_name,
        'tags': facet_tags,
        'parent_collection_names': facet_parent_collection_names,
        'number_of_voices': facet_number_of_voices,
    }


def get_paged_results(paginator, page_number):
    """
    Chubby chunk of code to try to get a page for the client
    :param paginator:
    :param page_number:
    :return:
    """
    try:
        paged_results = paginator.page(page_number)
    except paginate.PageNotAnInteger:
        try:
            paged_results = paginator.page(1)
        except paginate.EmptyPage:
            paged_results = []
    except paginate.EmptyPage:
        try:
            paged_results = paginator.page(paginator.num_pages)
        except paginate.EmptyPage:
            paged_results = []
    return paged_results


def get_page_number(request):
    """
    Get the page number from the HTTP GET parameters
    :param request:
    :return:
    """
    page_number = request.GET.get('page')
    try:
        page_number = int(page_number)
    except TypeError:
        pass
    return page_number


def format_search_result(result, facets, paginator, request):
    result["query"] = request.GET.urlencode()
    result['object_list'] = [item.__dict__ for item in result['object_list']]
    result['paginator'] = result['paginator'].__dict__
    result['paginator'].pop('query', None)
    result['paginator']['params'].update({'q': request.GET.get('q')})
    result['paginator'].update({'total_pages': paginator.num_pages})
    result['facets'] = facets.facet_counts
    result['facet_names'] = settings.FACET_NAMES
    del result['result']
    del result['paginator']['result']


class SearchView(generics.GenericAPIView):
    renderer_classes = (JSONRenderer, SearchViewHTMLRenderer)

    def get(self, request, *args, **kwargs):
        """
        Constructs a SolrSearch object using the search request; specifically,
        it parses and prepares the query and assigns it to s
        note: Filters, sorts, and other modifiers to solr search are
        handled in the helper script solrsearch.py
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        s = SolrSearch(request)
        # TODO add here when facets are decided
        facets = s.facets(facet_fields=['type',
                                        'composer_name',
                                        'tags',
                                        'parent_collection_names',
                                        'number_of_voices'])
        facets.facet_counts['facet_fields'] = parse_facets(facets)

        # The search() function belongs to SolrSearch, and simply returns the
        #  response for the aforementioned parsed and prepared query
        search_results = s.search()
        # Paginate results
        paginator = paginate.SolrPaginator(search_results)
        paged_results = get_paged_results(paginator, get_page_number(request))

        try:
            result = paged_results.__dict__
        except AttributeError:
            return Response({'object_list': []}, status=status.HTTP_200_OK)

        # Format the results
        format_search_result(result, facets, paginator, request)
        return Response(result, status=status.HTTP_200_OK)


class SearchAndAddToCartView(SearchView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """
        Constructs a SolrSearch object using the search request; specifically,
        it parses and prepares the query and assigns it to s
        note: Filters, sorts, and other modifiers to solr search are
        handled in the helper script solrsearch.py
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # Grab the cart
        cart = request.session.get('cart', {})
        # Set up the Solr connection
        s = SolrSearch(request)
        facets = s.facets(facet_fields=['type',
                                        'composer_name',
                                        'tags',
                                        'parent_collection_names',
                                        'number_of_voices'])
        facets.facet_counts['facet_fields'] = parse_facets(facets)
        search_results = s.search()
        # Paginate results
        paginator = paginate.SolrPaginator(search_results)
        # Loop through the result pages and add everything to the cart
        total = 0
        for page_number in range(paginator.num_pages):
            results = paginator.page(page_number + 1).result
            # Get the items from the page
            for search_object in results:
                print("adding {0}".format(search_object["uuid"]))
                add_item(search_object["type"], search_object["uuid"], cart)
                total += 1
        # Save the modified cart
        request.session['cart'] = cart
        return Response("{0} items added to cart.".format(total), status=status.HTTP_200_OK)
