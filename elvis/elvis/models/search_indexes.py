'''
from haystack.indexes import *
from haystack import site

from elvis.models.corpus import Corpus

class CorpusIndex(SearchIndex):
	text = CharField(document=True, use_template=True)
	title = CharField(model_attr='title')
	comment = CharField(model_attr='comment')

	def index_queryset(self): 
		return self.Corpus.objects.all()


site.register(Corpus, CorpusIndex)
'''