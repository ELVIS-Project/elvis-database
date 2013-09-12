import os, zipfile, tempfile, mimetypes
from datetime import datetime
from random import choice

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.core.servers.basehttp import FileWrapper
from django.core.files import File

import elvis.models 

from elvis.forms.entity import ComposerForm, CorpusForm, PieceForm, MovementForm, AttachmentForm
from elvis.forms.user import UserForm, InviteUserForm
from elvis.forms.project import ProjectForm, DiscussionForm, CommentForm, TodoForm

from django.contrib.auth.models import User
from elvis.models.composer import Composer
from elvis.models.corpus import Corpus
from elvis.models.attachment import Attachment
from elvis.models.piece import Piece
from elvis.models.download import Download
from elvis.models.movement import Movement
from elvis.models.tag import Tag

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


def corpus_handler(request):
	picture = choice(os.listdir(os.path.abspath('elvis/media/generics/corpora')))
	if request.method == 'POST':
		form = CorpusForm(request.POST)
		if form.is_valid():
			clean_form = form.cleaned_data
			# use **qwargs for additional data? 
			corpus = Corpus(title=clean_form['title'], 
							comment=clean_form['comment'], 
							picture=clean_form['picture'],
							creator_id=400 )
			corpus.save()
			return HttpResponseRedirect('/uploads/success/')
	else:
		form = CorpusForm( initial={'title': 'Corpus name', 
        							'comment': 'This corpus is about...' } )
	return form, picture

def create_corpus(request):
	form, picture = corpus_handler(request)
	return render(request, 'forms/corpus.html', {'form': form, 'picture':picture})

def create_corpus_large(request):
	form, picture = corpus_handler(request)
	return render(request, 'forms/corpus_large.html', {'form': form, 'picture':picture})

def tag_handler(tags):
	new_tags = []
	if tags:
		tag_list = map(lambda tag: str(tag.strip()), tags.split(','))
		tag_objects = Tag.objects.all()
		if tag_objects:
			for tag_object in tag_objects:
				found = False
				for tag in tag_list:
					if tag == str(tag_object.name).strip():
						new_tags.append(tag_object)
						found = True
						break
				if not found:
					tag_instance = Tag(name=tag)
					tag_instance.save()
					new_tags.append(tag_instance)
		else:
			for tag in tag_list:
				tag_instance = Tag(name=tag)
				tag_instance.save()
				new_tags.append(tag_instance)
	return new_tags

# Finds associated object. Associated object MUST exist
# Ex: If doesn't find corpus that already exists, returns none
def object_handler(model, string):
	if string:
		for m in model.objects.all():
			if str(m.title) == str(string):
				return m
	return None

# Finds associated composer. If composer does not exist creates new composer 
def composer_handler(composer):
	if composer:
		for c in Composer.objects.all():
			if str(c.name) == str(composer):
				return c
		composer_instance = Composer(name=composer)
		composer_instance.save()
		return composer_instance
	return None

def date_handler(datestr): 
	if datestr:
		try:
			return datetime.strptime(str(datestr), '%m-%d-%y')
		except:
			return datetime.strptime(str(datestr), '%m-%d-%Y')
	else:
		return None

# Remember that these are all in lists except for upfile
def create_movement_object(upfile, piece, composer, corpus, description, comments, voices, tags, dates, titles, voice, date, descrip, tag, comment, title):
	user = User.objects.get(pk=40) 	# Hardcoded for now

	final_tags = tags+tag
	final_description = descrip if descrip else description
	final_date = date_handler(date) if date else date_handler(dates)
	final_voice = voice if voice else voices
	final_comment = comment if comment else comments
	final_title = title if title else titles

	# Ugh...fix date stuff
	if final_date == '':
		final_date = datetime.today()

	# First create attachment 
	attachment = file_handler_helper(upfile, final_description)

	# Handle tags, composer, corpus
	tag_objects = tag_handler(final_tags)
	composer_obj = composer_handler(composer)
	corpus_obj = object_handler(Corpus, corpus)

	# Next create the movement
	mov = Movement( title=final_title, 
					composer=composer_obj,
					uploader=user,
					piece =piece,
					corpus=corpus_obj,
					number_of_voices=final_voice,
					comment=final_comment,
					date_of_composition=final_date )
	mov.save()

	# Add attachment to movement
	mov.attachments.add(attachment)
	mov.save()

	# Add tags to movement
	for tag in tag_objects:
		mov.tags.add(tag)
	mov.save()


# Handle extra movement files in piece upload if there are any
def movement_files_handler(post, files, piece):
	# First get the piece information. Some of this will be used in creating movements
	title = post.get('title')
	composer = post.get('composer')
	corpus = post.get('corpus')
	description = post.get('description')
	comment = post.get('comment')
	voices = post.get('number_of_voices')
	tags = post.get('tags')
	dates = post.get('date_of_composition')

	# If there are movements create them, regardless of presence of piece attachment
	if files.get('upload[]'):
		upfiles = files.getlist('upload[]')
		num_files = len(upfiles)
		for x in range(0,num_files):
			voice = 'mov-num-voices'+str(x)
			descrip = 'mov-descrip'+str(x)
			tag = 'mov-tags'+str(x)
			date = 'mov-date'+str(x)
			comment = 'mov-comment'+str(x)
			title = 'mov-title'+str(x)

			create_movement_object(upfiles[x], piece, composer, corpus, description, comment, voices, tags, dates, title, post.get(voice), post.get(date), post.get(descrip), post.get(tag), post.get(comment), post.get(title))

	# If there is only a piece attachment, create this and return
	elif files.get('attachment'):
		return [file_handler_helper(files.get('attachment'), description)]

	# If there are neither or just created movements return empty list
	return []

# TODO: Error handling for tag list 
# TODO: Error handling for corpus - must exist
# TODO: If corpus does not exist, should raise error
def create_piece(request):
	if request.method == 'POST':
		form = PieceForm(request.POST, request.FILES)
		if form.is_valid():
			clean_form = form.cleaned_data
			# Hardcoded user for now
			uploader = User.objects.get(pk=40)

			# Handle tags
			tags = tag_handler(clean_form['tags'])

			# Handle composer and corpus
			composer = composer_handler(clean_form.get('composer'))
			corpus = object_handler(Corpus, clean_form.get('corpus'))
			date = date_handler(clean_form.get('date_of_composition'))

			# Create piece
			piece = Piece(title=clean_form['title'],
							composer=composer,
							corpus=corpus,
							date_of_composition=date,
							number_of_voices=clean_form.get('number_of_voices'),
							comment=clean_form.get('comment'),
							uploader=uploader )
			piece.save()

			attachments = []
			# Create movements associated with piece (if any)
			# Also return attachment associated with piece if possible
			attachments.extend(movement_files_handler(request.POST, request.FILES, piece))

			# Add tags to piece
			for tag in tags:
				piece.tags.add(tag)
			piece.save()

			# Add attachments to piece
			for attachment in attachments:
				piece.attachments.add(attachment)
			piece.save()

	else:
		form = PieceForm(initial={'title':'Piece title', 
									'composer': 'Composer', 
									'corpus': 'Corpus',
									'date_of_composition':'date of composition',
									'comment': 'Add a comment...',
									'tags': 'Comma-separated list of tags',
									'description':'Description of piece file...'})
	return render(request, 'forms/piece.html', {'form':form})

# TODO: error handling for tag list
# TODO: error handling for piece - must exist
def create_movement(request):
	if request.method == 'POST':
		form = MovementForm(request.POST, request.FILES)
		if form.is_valid():
			clean_form = form.cleaned_data
			# Hardcoded user for now
			uploader = User.objects.get(pk=40)

			# Get and create attachment if possible
			try:
				attach = clean_form['attachment']
				attachment = Attachment()
				attachment.save()
				attachment.attachment = attach
				attachment.uploader = uploader
				attachment.description = clean_form.get('description')
				attachment.save()
			except KeyError:
				attachment = None

			# Handle tags
			tags = tag_handler(clean_form['tags'])

			# Handle objects
			piece = object_handler(Piece, clean_form['piece'])
			corpus = object_handler(Corpus, clean_form.get('corpus'))
			composer = composer_handler(clean_form.get('composer'))

			# Create movement
			movement = Movement(title=clean_form['title'],
							composer=composer,
							corpus=corpus,
							piece=piece,
							date_of_composition=clean_form.get('date_of_composition'),
							number_of_voices=clean_form.get('number_of_voices'),
							comment=clean_form.get('comment'),
							attachment=attachment,
							tags=tags,
							uploader=uploader )
			movement.save()
	else:
		form = MovementForm(initial={'title':'Movement title', 
									'composer': 'Composer', 
									'corpus': 'Corpus',
									'piece': 'Piece',
									'date_of_composition':'date of composition',
									'comment': 'Add a comment...',
									'tags': 'Comma-separated list of tags',
									'description':'Description of movement file...'})
	return render(request, 'forms/movement.html', {'form':form})

# TODO: Send email to each email in invited list 
def user_handler(users):
	emails = map(lambda email:str(email).strip(), users.split(','))
	return emails

# TODO : Send email to users
def create_project(request):
	if request.method == 'POST':
		form = ProjectForm(request.POST)
		clean_form = form.cleaned_data

		# Get users invited to this project
		users = user_handler(clean_form.get('users'))

		# Create project - name, descrip, users
		project = Project(name=clean_form['title'],
							description=clean_form.get('description') )
		# Save for now, add users later 
		project.save()
	else:
		form = ProjectForm(initial={'name':'Name this project',
									'description':'Describe this project' })
	return render(request, 'forms/project.html', {'form':form})


'''
Views that upload files to file system
'''
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
	f.uploader = User.objects.get(pk=40) 	# Hardcoded for now
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
			user = User.objects.get(pk=40)	# Hardcoded for now
			dl = Download(user=user, attachment=attachment)
			dl.save()
		return HttpResponseRedirect('/downloads/')
	return render(request, 'forms/save.html')

# Used for only individual piece attachments
def save_movement(request, pk):
	if request.method == 'POST':
		movement = Movement.objects.get(pk=pk)
		for attachment in movement.attachments.all():
			user = User.objects.get(pk=40)	# Hardcoded for now
			dl = Download(user=user, attachment=attachment)
			dl.save()
		return HttpResponseRedirect('/downloads/')
	return render(request, 'forms/save.html')


'''
# Download file without loading all into memory (chunks of 8KB)
def download_file(filename):
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

# Create zip file on disk and download it in chunks of 8KB
def download_zipfile(request):
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for index in range(10):
        filename = __file__ # Select your files here.                           
        archive.write(filename, 'file%d.txt' % index)
    archive.close()
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=test.zip'
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
'''

		
