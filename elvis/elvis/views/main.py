import sys, operator
import elvis.models

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.models import User
from elvis.models.attachment import Attachment
from elvis.models.composer import Composer
from elvis.models.download import Download
from elvis.models.comment import Comment
from elvis.models.userprofile import UserProfile
from elvis.models.project import Project
from elvis.models.todo import Todo
from elvis.models.discussion import Discussion
from elvis.models.comment import Comment
from elvis.models.query import Query
from elvis.views.corpus import Corpus
from elvis.views.piece import Piece
from elvis.views.movement import Movement

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

# USER = User.objects.get(pk=40)
USER = None

# Default number of results per page. Used for pagination 
RESULT_PER_PAGE = 25

# Render the home page 
def home(request):
    return render(request, "home.html", {})

# Render the upload page 
def upload(request):
	return render(request, "upload.html", {})

# TOOD: Need to extract model information from QuerySet
def get_model(qs):
    return None

def relevant_field(field): 
    field = str(field)
    return 'CharField' in field or 'TextField' in field

# Partition data into rows. Used for template organization
def partition(data, row):
    partitioned_data = []
    for x in range(0, len(data), row):
        partitioned_data.append(data[x:x+row])
    return partitioned_data

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
# TODO: Can reduce complexity by hardcoding DateField relations? 
# TODO: Can get class names from meta class. what about predefined classes like User? 
def filter_dates(querysets, start, end, alldb=False):
    # This means should only look at dates related to objects found
    if not alldb:
        # Iterate through each query set and get all related pk's w/ dates
        for queryset in querysets:
            for result in queryset:


    # Otherwise just return all objects in this range
    else:
'''

'''
def filter_voices(results, voices, alldb=False):
    # This means should only look at voices related to objects found
    if results:
        
    # Otherwise just return all objects with this number of voices
    else:
'''


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
USER PROFILES
'''

# Render list of user profiles
def user_profiles(request):
    userprofiles = UserProfile.objects.all()
    userprofiles_list = partition(userprofiles, 4)
    return render(request, 'userprofile/userprofile_list.html', {'content': userprofiles_list, 'length':len(userprofiles)})

def user_view(request, pk):
    user = UserProfile.objects.filter(pk=pk)[0]
    return render(request, 'userprofile/userprofile_detail.html', {'content':user})

'''
PROJECTS
'''

def projects_list(request):
    projects = Project.objects.all()
    projects_list = partition(projects, 3)
    return render(request, 'project/project_list.html', {'projects': projects_list, 'length':len(projects)})

def project_view(request, pk):
    project = Project.objects.filter(pk=pk)[0]
    todos = Todo.objects.filter(project_id=pk)
    discussions = Discussion.objects.filter(project_id=pk)
    comments = {}
    for discussion in discussions:
        comments[discussion.id] = Comment.objects.filter(discussion_id=discussion.id).order_by('-created')
    context = {'content':project, 
                'todos': todos, 
                'discussions':discussions, 
                'comments':comments}
    return render(request, 'project/project_detail.html', context)

def project_participants(request, pk):
    project = Project.objects.filter(pk=pk)[0]
    return render(request, 'project/project_participants.html', {"content": project})

def project_discussions(request, pk):
    project = Project.objects.filter(pk=pk)[0]
    discussions = Discussion.objects.filter(project_id=pk)
    num_comments = {}
    for discussion in discussions:
        num_comments[discussion.id] = Comment.objects.filter(discussion_id=discussion.id).count()
    context = {"project": project, 
                "discussions": discussions,
                "comments": num_comments}
    return render(request, 'project/project_discussions.html', context)

def discussion_view(request, pk, did):
    if request.method == "POST":
        comment = request.POST.get('comment')
        obj = Comment(name='', text=comment, user_id=400, discussion_id=did)
        obj.save()
    project = Project.objects.get(pk=pk)
    discussion = Discussion.objects.get(pk=did)
    comments = Comment.objects.filter(discussion_id=did)
    context = {"project": project, "discussion": discussion, "comments": comments}
    return render(request, 'discussion/discussion_detail.html', context)

'''
MODEL LISTS
'''

# Utility method to sort objects by filters
def sort_objects(object_name, val):
    if val is None or val == u"0" or val == u"most":
        return object_name.objects.all()
    else:
        return object_name.objects.all().order_by(val)

# Utility method to paginate a query set 
def paginate(objects, GET, num=RESULT_PER_PAGE):
    paginator = Paginator(objects, num)
    page = GET.get("page")
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
    return object_list

def corpora_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_corpus(request.POST.getlist('save-items'))

    corpora = paginate(sort_objects(Corpus, val), request.GET)

    if val == u'most':
        corp = map(lambda corpus:(Piece.objects.filter(corpus_id=corpus.id).count(), corpus), corpora)
        corp.sort()
        corpora = paginate([c[1] for c in corp], request.GET)

    return render(request, 'corpus/corpus_list.html', {"content":corpora})

def corpora_list_min(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_corpus(request.POST.getlist('save-items'))

    corpora = paginate(sort_objects(Corpus, val), request.GET)

    if val == u'most':
        corp = map(lambda corpus:(Piece.objects.filter(corpus_id=corpus.id).count(), corpus), corpora)
        corp.sort()
        corpora = paginate([c[1] for c in corp], request.GET)

    return render(request, 'corpus/corpus_list_min.html', {"content":corpora})

# TODO: when sort value = most
def composer_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_composer(request.POST.getlist('save-items'))
    if val == u'most':
        comp = []

    composers = paginate(sort_objects(Composer, val), request.GET)
    pieces = {}

    for composer in composers:
        p = map(lambda x:x.title, list(Piece.objects.filter(composer_id=composer.id)))[:15]
        if val == u'most':
            comp.append( (len(p), composer) )
        if p:
            pieces[composer.id] = ', '.join(p)+'...'
        else:
            pieces[composer.id] = ''

    if val == u'most':
        comp.sort(reverse=True)
        composers = paginate([c[1] for c in comp], request.GET)

    context = {"content": composers, "pieces":pieces }

    return render(request, 'composer/composer_list.html', context)

# TODO: when sort value = most
def composer_list_min(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_composer(request.POST.getlist('save-items'))
    if val == u'most':
        comp = []

    composers = paginate(sort_objects(Composer, val), request.GET)

    if val == u'most':
        comp.sort(reverse=True)
        composers = paginate([c[1] for c in comp], request.GET)

    context = {"content": composers }

    return render(request, 'composer/composer_list_min.html', context)

def piece_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_pieces(request.POST.getlist('save-pieces'))

    pieces = paginate(sort_objects(Piece, val), request.GET, num=40)

    return render(request, 'piece/piece_list.html', {"content": pieces})

def movement_list(request):
    val = None
    if request.method == "POST":
        val = request.POST.get('sorting')
        save_movements(request.POST.getlist('save-movements'))

    movements = paginate(sort_objects(Movement, val), request.GET, num=40)

    return render(request, 'movement/movement_list.html', {"content":movements})

# Download has attachment associated with either piece or movement
def download_list(request):
    if request.method == 'POST':
        dl_ids = request.POST.getlist('download-item')
        for dl_id in dl_ids:
            Download.objects.get(pk=int(str(dl_id))).delete()

    downloads = paginate(Download.objects.all(), request.GET, num=40)

    return render(request, 'download/download_list.html', {"content": downloads})

'''
SAVE Utility functions
'''

# TODO: This should probably take a piece object not str/int
# Causes superfluous querying of db from save_corpus/composer/etc
def save_piece(piece):
    p = Piece.objects.get(pk=int(piece))
    # Save all of a piece's movements
    movs = Movement.objects.filter(piece_id=int(piece))
    if movs:
        for m in movs.all():
            for attachment in m.attachments.all():
                dl = Download(user=USER, attachment=attachment)
                dl.save()
    # If piece has attachment, save this
    else:
        attachments = p.attachments.all()
        if attachments:
            for attachment in attachments:
                dl = Download(user=USER, attachment=attachment)
                dl.save()

def save_movement(movement):
    m = Movement.objects.get(pk=int(movement))
    for attachment in m.attachments.all():
        dl = Download(user=USER, attachment=attachment)
        dl.save()

def save_pieces(pieces):
    if pieces:
        for piece in pieces:
            save_piece(piece)

def save_movements(movements):
    if movements:
        for movement in movements:
            save_movement(movement)

def save_corpus(corpora):
    if corpora:
        for corpus in corpora:
            pieces = Piece.objects.filter(corpus_id=int(corpus))
            for piece in pieces:
                save_piece(piece.id)

def save_composer(composers):
    if composers:
        for composer in composers:
            pieces = Piece.objects.filter(composer_id=int(composer))
            for piece in pieces:
                save_piece(piece.id)

'''
MODEL DETAILS
'''

def corpus_view(request, pk):
    if request.method == 'POST':
        save_pieces(request.POST.getlist('piece-save'))
        save_movements(request.POST.getlist('movement-save'))
        dl_piece = request.POST.getlist('piece-download')
        dl_movement = request.POST.getlist('movement-download')

        return HttpResponseRedirect('/downloads/')

    corpus = Corpus.objects.get(pk=pk)
    pieces = Piece.objects.filter(corpus_id=pk)
    movements = {}
    for piece in pieces:
        movements[piece.id] = Movement.objects.filter(piece_id=piece.id)
    context = {'content':corpus,
                'pieces':pieces,
                'movements':movements,
                'url': request.build_absolute_uri()}
    return render(request, 'corpus/corpus_detail.html', context)

def composer_view(request, pk):
    if request.method == 'POST':
        save_pieces(request.POST.getlist('save-pieces'))
        save_movements(request.POST.getlist('save-movements'))
        dl_piece = request.POST.getlist('download-pieces')
        dl_movement = request.POST.getlist('download-movements')

        return HttpResponseRedirect('/downloads/')

    composer = Composer.objects.get(pk=pk)
    pieces = Piece.objects.filter(composer_id=pk)
    movements = {}
    for piece in pieces:
        movements[piece.id] = Movement.objects.filter(piece_id=piece.id)
    context = {'content':composer,
                'pieces':pieces,
                'movements':movements,
                'url': request.build_absolute_uri()}
    return render(request, 'composer/composer_detail.html', context)

def piece_view(request, pk):
    piece = Piece.objects.get(pk=pk)
    movements = Movement.objects.filter(piece_id=pk)
    url = request.build_absolute_uri()
    return render(request, 'piece/piece_detail.html', {'content':piece, 'movements':movements, 'url':url})

def movement_view(request, pk):
    movement = Movement.objects.get(pk=pk)
    url = request.build_absolute_uri()
    return render(request, 'movement/movement_detail.html', {'content':movement, 'url':url})

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