
import elvis.models

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponseRedirect

from elvis.models.download import Download
from elvis.models.userprofile import UserProfile

from elvis.utils.helpers import sendemails, createTempUser

'''
def get_models(models):
    return filter(lambda mod: not mod.startswith('__') and mod[0].isupper(), models)

def model_dict(models):
    model_info = {}
    for model in models:
        model_class = getattr(elvis.models, model)
        model_info[model_class] = model_class._meta.fields
    return model_info

HTTP_METHODS = ['GET', 'PUT', 'POST', 'HEAD', 'TRACE', 'DELETE', 'OPTIONS']
MODELS = get_models(dir(elvis.models))
MODEL_INFO = model_dict(MODELS)
'''

USER = UserProfile.objects.get(id=90)
URL = "http://localhost:8000/"

# Render the home page 
def home(request):
    return render(request, "home.html", {})

# Render the login page 
def user_login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return HttpResponseRedirect('/home/')
        else:
            context = {"error_message": "Wrong username or password."}
    return render(request, 'registration/login.html', context)

# TODO: If want to save anything from current session, do that after logout
def user_logout(request):
    logout(request)

# TODO: Message body 
def request_permission(request):
    context = {}
    if request.method == 'POST':
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        email = request.POST['email']
        # First create a temporary (inactive) user object for this user
        # This will be activated once the admin sets permissions and once the user receives a confirmation email 
        user, userprofile = createTempUser(first_name, last_name, email)
        # Then send email to admin 
        subject = first_name + " " + last_name + " would like to join ELVIS."
        message = "Go to " + URL + "registration" + " to allow or disallow the user to join and set permissions."
        val = sendemails(email, [USER.user.email], subject, message)
        if val:
            context = {'success': 'Your email has been sent.'}
        else:
            context = {'failure': 'Something went wrong.'}
    return render(request, 'registration/permission.html', context)

# Render the upload page 
def upload(request):
	return render(request, "upload.html", {})

# TOOD: Need to extract model information from QuerySet
def get_model(qs):
    return None

def relevant_field(field): 
    field = str(field)
    return 'CharField' in field or 'TextField' in field


# TODO: Can reduce complexity by hardcoding FK-relations? 
# TODO: This is bad since PKs can be the same within different tables, so REDO THIS 
# For each object in each queryset, get PK and query db for all objects where FK=PK
def get_related(querysets, filters):
    # If no filters are specified, use all models
    # Otherwise only look within specified filters 
    if not filters:
        filters = MODELS
    results = []
    for queryset in querysets:
        # Get primary key of each object in query set 
        keys = map(lambda q: q.pk, list(queryset))
        # For each model get foreign key fields
        for model in filters:
            model = getattr(elvis.models, model)
            fields = filter(lambda field: 'ForeignKey' in str(field), model._meta.fields)
            for pk in keys:
                # Create query key, value pairs of FK name and PK
                query_vals = map(lambda field: (field.name, pk), fields)
                if query_vals:
                    # Create conjunction of fields for query 
                    qset = reduce(operator.or_, (Q(**{field: query}) for field, query in query_vals))
                    results.append(model.objects.filter(qset))
    return results


'''
SEARCH
'''

# Must search CharField, TextField of all models in specified filters
def search(query, exclude, filters):
    # Exclude should be comma-separated list
    excluded_queries = []
    if exclude:
        excluded_queries = exclude.split(',')
    # If no filter specified, just look through all the models
    if not filters:
        filters = MODELS
    results = []
    for category in filters:
        # Get class associated with filter
        model = getattr(elvis.models, category)
        included = []
        excluded = []
        result = []
        if query:
            # Get relevant attributes of this class
            fields = filter(lambda field: relevant_field(field), model._meta.fields)
            # Create query key, value pairs for included and excluded search params
            included = map(lambda field: (field.name+'__icontains', query), fields)
        for eq in excluded_queries:
            for field in fields:
                excluded.append( (field.name+'__icontains', eq) )

        # Create conjunction of fields for query 
        if included:
            qset_inc = reduce(operator.or_, (Q(**{field: query}) for field, query in included))  
            result = model.objects.filter(qset_inc)  
        if excluded:
            qset_exc = reduce(operator.or_, (Q(**{field: query}) for field, query in excluded))
            result = result.exclude(qset_exc)
        if result:
            results.append(result)
    return results

# TODO: Need to return items related to search param
# TODO: get filters by class or something 
# TODO: Add discussion/projects/comments filters
# TODO: Remove redundancies 
# TODO: Fix exclude - isn't really working 
# Query database based on search terms
def search_view(request):
    if request.method == "GET":
        query = request.GET.get('search')
        exclude = request.GET.get('exclude')
        start_year = request.GET.get('start-year')
        end_year = request.GET.get('end-year')
        piece = request.GET.get('piece')
        movement = request.GET.get('movement')
        composer = request.GET.get('composer')
        user = request.GET.get('user')
        discussion = request.GET.get('discussion')
        log = request.GET.get('log')
        voices = request.GET.get('num-voices')

        # First get all valid query parameters
        querylist = [query, exclude, start_year, end_year, piece, movement, composer, user, discussion, log, voices]
        querylist = filter(lambda x: not (x is u'' or x is None), querylist)

        # Now save the query to the database
        q = Query(query=' '.join(querylist))
        q.save()

        # Create list of filters
        raw_filters = [piece, movement, composer, user, discussion, log]
        filters = filter(lambda x:x is not None and x.title() in MODELS, raw_filters)

        # If there is a basic query or exclude statement, search for or omit it or both
        if query or exclude:
            results = search(query, exclude, filters)
            # Now get all related objects 
            results += get_related(results, filters)
            # Now filter further on dates
           # results = filter_dates(results, start_year, end_year)
            # Now filter further on #of voices
           # results = filter_voices(results, voices)

        # Otherwise get all objects in specified categories
        elif filters:
            filter_classes = map(lambda filt: getattr(elvis.models, filt.title()), filters)
            results = map(lambda filt_class: filt_class.objects.all(), filter_classes)
            # Now apply date/voice filters ot these query sets
           # results = filter_dates(results, start_year, end_year)
           # results = filter_voices(results, voices)

        # Get all objects that have DateFields in this date range 
       # elif start_year or end_year:
       #     results = filter_dates(None, start_year, end_year, alldb=True)

        # Get all pieces/movements from db that have this number of voices 
       # elif voices: 
       #     results = filter_voices(None, voices, alldb=True)
    
    results = [result for result in results if len(result) > 0]
    final_results = []
    for result in results:
        final_results.extend(result)
    num_results = len(final_results)
    return render(request, 'search_results.html', {"results": final_results, "query":querylist, "num_results": num_results})


def queries(request):
    queries = Query.objects.all()
    return render(request, 'query.html', {"content": queries})



'''
DOWNLOADS
'''

# Used across html files to save items to download later
# TODO: How to get current user? 
def save_downloads(request):
    if request.method == 'POST':
        items = request.getlist("items")
        # Need to save these items to the database
        for item in items:
        	obj = Download(item)
        	obj.save()
    # Now render downloads page 
    return render(request, "download.html", {})