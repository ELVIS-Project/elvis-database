import os, zipfile, tempfile, mimetypes
from datetime import datetime
from random import choice

import urlparse

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status

import elvis.models 

from elvis.forms.entity import ComposerForm, PieceForm, MovementForm, AttachmentForm
from elvis.forms.project import ProjectForm


from django.contrib.auth.models import User
from elvis.models.composer import Composer
from elvis.models.collection import Collection
from elvis.models.attachment import Attachment
from elvis.models.piece import Piece
from elvis.models.download import Download
from elvis.models.movement import Movement
from elvis.models.tag import Tag
from elvis.models.project import Project

'''
Views that create and add an entity to the database 
'''


def create_composer(request):
    picture = choice(os.listdir(os.path.abspath('elvis/media/generics/composers')))
    if request.method == 'POST':
        form = ComposerForm(request.POST)
        if form.is_valid():
            clean_form = form.cleaned_data
            # use **qwargs for additional data? 
            composer = Composer(name=clean_form['name'], 
                                birth_date=date_handler(clean_form.get('birth_date')), 
                                death_date=date_handler(clean_form.get('death_date')) )
            composer.save()
            return HttpResponseRedirect('/uploads/success/')
    else:
        form = ComposerForm( initial={'name': 'Composer name', 
                                    'birth_date': 'birth date', 
                                    'death_date': 'death date'} )
    return render(request, 'forms/composer.html', {'form': form, 'picture':picture})



# TODO: Send email to each email in invited list 
def user_handler(users):
    emails = map(lambda email:str(email).strip(), users.split(','))
    return emails

# TODO : Send email to users
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            clean_form = form.cleaned_data

            # Get users invited to this project
            users = user_handler(clean_form.get('users'))

            # Create project - name, descrip, users
            project = Project(name=clean_form['name'],
                                description=clean_form.get('description') )
            # Save for now, add users later 
            project.save()
            return HttpResponseRedirect('/projects/')
    else:
        form = ProjectForm(initial={'name':'Name this project',
                                    'description':'Describe this project' })
    return render(request, 'forms/project.html', {'form':form})


def inviteUsersToProject(request): 
    return render(request, 'project/snippets/invite_users.html', {})

def deleteProject(request):
    return render(request, 'project/snippets/delete_project.html', {})

'''
Views that upload files to file system
'''
#@login_required
def upload_file(request):
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            file_handler(request.POST, request.FILES)
            return HttpResponseRedirect('/uploads/success')
    else:
        form = AttachmentForm(initial={'description':'File description'})
    return render(request, 'forms/upload.html', {'form': form})

# Handles upload of a file, whether single or zip
def file_handler(fileobject, description):
    # If we have zip file upload multiple files with same description
    if fileobject.name.endswith('.zip'):
        for filename,content in fileiterator(fileobject):
            f = file_handler_helper(filename, description)
    else:
        f = file_handler_helper(fileobject, description)

# Saves an attachment and uploads file
def file_handler_helper(uploadedfile, description):
    f = Attachment()
    # Save first to generate pk for random file system
    f.save()
    f.uploader = User.objects.get(pk=40)    # Hardcoded for now
    f.attachment = uploadedfile
    if description:
        f.description = description
    f.save()
    return f

# Utility method that iterates over zip file
def fileiterator(zipf):
    with zipfile.ZipFile(zipf, "r", zipfile.ZIP_STORED) as openzip:
        filelist = openzip.infolist()
        for f in filelist:
            yield(f.filename, openzip.read(f))
        

'''
View that deletes a model
'''

# All models except for file-related models and user models have title/name
def get_field(record):
    try:
        return record.title
    except AttributeError:
        return record.name

# TODO: need correct permissions, make sure associated files are deleted
def delete_model(request, entity, pk):
    entity = entity[:len(entity)-1].capitalize()
    model = getattr(elvis.models, entity)
    pk = int(str(pk))
    record = model.objects.get(pk=pk)
    name = get_field(record)
    context = {"error": None, "name": name, "entity": entity}
    if request.method == 'POST':
        record.delete()
        return HttpResponseRedirect('/uploads/success')
    else:
        return render(request, 'forms/delete.html', context)

'''
Views that download/save files
'''

def download_piece(request, pk):
    if request.method == 'POST':
        piece = Piece.objects.get(pk=pk)
        piece.number_of_downloads += 1
        piece.save()
        attachments = piece.attachments.all()
        if len(attachments) == 1:
            filename = '/media/attachments/'+str(attachments[0].attachment.name)
            #return HttpResponseRedirect(filename)
            download_file(attachments[0])
        else:
            download_zip(attachments)
    return render(request, 'forms/download.html')

def download_movement(request, pk):
    if request.method == 'POST':
        movement = Movement.objects.get(pk=pk)
        movement.number_of_downloads += 1
        movement.save()
        attachments = movement.attachments.all()
        if len(attachments) == 1:
            filename = '/media/attachments/'+str(attachments[0].attachment.name)
            #return HttpResponseRedirect(filename)
            download_file(attachments[0])
        else:
            download_zip(attachments)
    return render(request, 'forms/download.html')

def download_file(attachment):
    #path_to_file = os.path.realpath('media/attachments/'+str(attachment.attachment.name))
    path_to_file = 'elvis/media/attachments/'+str(attachment.attachment.name)
    myfile = FileWrapper(open(path_to_file, 'r'))
    response = HttpResponse(myfile, content_type=mimetypes.guess_type(path_to_file)[0])
    #content_disp = 'attachment; filename='+str(attachment.attachment.name)
    content_disp = 'attachment; filename='+path_to_file
    response['Content-Disposition'] = content_disp
    return response

# Used for only individual movement attachments 
def save_piece(request, pk):
    if request.method == 'POST':
        piece = Piece.objects.get(pk=pk)
        for attachment in piece.attachments.all():
            user = User.objects.get(pk=40)  # Hardcoded for now
            dl = Download(user=user, attachment=attachment)
            dl.save()
        return HttpResponseRedirect('/downloads/')
    return render(request, 'forms/save.html')

# Used for only individual piece attachments
def save_movement(request, pk):
    if request.method == 'POST':
        movement = Movement.objects.get(pk=pk)
        for attachment in movement.attachments.all():
            user = User.objects.get(pk=40)  # Hardcoded for now
            dl = Download(user=user, attachment=attachment)
            dl.save()
        return HttpResponseRedirect('/downloads/')
    return render(request, 'forms/save.html')
