""" Search class """

import solr
import datetime
from settings import SOLR_SERVER

import elvis.models

from elvis.models.composer import Composer
from elvis.models.corpus import Corpus
from elvis.models.tag import Tag
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from django.contrib.auth.models import User


class Search:
	def __init__(self, POST):
		#self.server = solr.SolrConnection(SOLR_SERVER)
		self.operator = POST.get("onoffswitch")
		self.query = POST.get("searchinput")
		self.filters = self.setFilters(POST.get("filters"))
		self.date_range = self.setDateRange(POST.get("date_range"))
		self.composers = self.setIndividualModels(POST.get("composers"))
		self.corpora = self.setIndividualModels(POST.get("corpora"))
		self.tags = self.setIndividualModels(POST.get("tags"))
		self.uploaders = self.setIndividualModels(POST.get("uploaders"))
		self.voices = self.setIndividualModels(POST.get("voices"))
		self.composer_results = {"pieces": [],
								"movements": [] }
		self.corpus_results = {"pieces": [],
								"movements": []}
		self.tag_results = {"pieces": [],
							"movements": []}
		self.uploader_results = {"pieces": [],
								"movements": []}
		self.date_results = {"pieces": [],
							"movements": [],
							"composers": [] }
		self.voice_results = {"pieces":[],
							"movements": [] }
		self.type_of_query = ""

	''' Some helper parsing methods ''' 
	def setDateRange(self, datestr):
		try:
			return datestr.split(' - ')
		except:
			return None

	def setIndividualModels(self, modelstr):
		try:
			models = modelstr.split(',')
			return models[:len(models)-1]
		except:
			return None

	def setFilters(self, filterstr):
		filters = {}
		try:
			models = map(lambda modelstr: str(modelstr), filterstr.split(','))
			# Ignore voices since not a model
			if 'voice' in models:
				models.remove('voice')
			for model in models[:len(models)-1]:
				filters[model] = getattr(elvis.models, model)
			# Create actual models out of all of these 
			return filters
		except:
			return None


	''' Search methods '''

	# Main search departure method 
	def search(self):
		# Case 1: input query is empty
		if self.query == u"Search" or self.query == "":
			if self.operator == u"on":
				self.type_of_query = "EMPTY_AND"
				return self.empty_search_and()
			else:
				print "doing empty or search"
				self.type_of_query = "EMPTY_OR"
				return self.empty_search_or()
		# Case 2: query exists
		else:
			if self.operator == u"on":
				self.type_of_query = "QUERY_AND"
			else:
				self.type_of_query = "QUERY_OR"
			return None

	# If there is no input query and operator is conjunction return intersection of filters
	def empty_search_and(self):
		return None

	def or_composer_helper(self, idlist):
		for modelID in idlist:
			print modelID
			print Piece.objects.filter(composer_id=modelID)
			print Movement.objects.filter(composer_id=modelID)
			self.composer_results['pieces'].append(Piece.objects.filter(composer_id=modelID))
			self.composer_results['movements'].append(Movement.objects.filter(composer_id=modelID))
		print "Done composer helper"
		return

	def or_corpus_helper(self, idlist):
		for modelID in idlist:
			self.corpus_results['pieces'].append(Piece.objects.filter(corpus_id=modelID))
			self.corpus_results['movements'].append(Movement.objects.filter(corpus_id=modelID))

	def or_uploader_helper(self, idlist):
		for userID in idlist:
			self.uploader_results['pieces'].append(Piece.objects.filter(uploader_id=userID))
			self.uploader_results['movements'].append(Movement.objects.filter(uploader_id=userID))

	def or_tag_helper(self, tags):
		return None

	def or_voice_helper(self, voices):
		for voice in voices:
			self.voice_results['pieces'].append(Piece.objects.filter(number_of_voices=voice))
			self.voice_results['movements'].append(Movement.objects.filter(number_of_voices=voice))

	def or_date_helper(self, dates):
		first = int(dates[0])
		second = int(dates[1])
		if first <= second:
			start = first
			end = second
		else:
			start = second
			end = first
		start_date = datetime.date(start, 1, 1)
		end_date = datetime.date(end, 12, 31)
		self.date_results['composers'].append(Composer.objects.filter(birth_date__range=(start_date, end_date)))
		self.date_results['pieces'].append(Piece.objects.filter(composition_start_date__range=(start_date, end_date)))
		self.date_results['movements'].append(Movement.objects.filter(composition_start_date__range=(start_date, end_date)))

	# If there is no input query and operator is disjunction return union of filters
	# Individual selections within filter override the filter itself
	def empty_search_or(self):
		print "in empty or search method"
		# If there are individual composers selected, find these and ignore possible composer filter
		if self.composers:
			print "composer helper"
			self.or_composer_helper(self.composers)
		elif self.filters.get('Composer'):
			print "in here?"
			self.results.append(Composer.objects.all())

		print "overe here??" 

		# if self.corpora:
		# 	print "corpus helper"
		# 	self.or_corpus_helper(self.corpora)
		# elif self.filters.get('Corpus'):
		# 	self.results.append(Corpus.objects.all())

		# if self.uploaders:
		# 	print "uploader helper"
		# 	self.or_uploader_helper(self.uploaders)
		# elif self.filters.get('Uploader'):
		# 	self.results.append(User.objects.all())

		# if self.tags:
		# 	print "tag helper"
		# 	self.or_tag_helper(self.tags)
		# elif self.filters.get('Tag'):
		# 	self.results.append(Tag.objects.all())

		# if self.voices:
		# 	print "voice helper"
		# 	self.or_voice_helper(self.voices)

		# self.or_date_helper(self.date_range)


	# TODO: Organize results by most queried 
	# TODO: Remove duplicates 
	def organize(self, results):
		return None





        
        