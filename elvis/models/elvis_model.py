import solr
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class ElvisModel(models.Model):
    """ A super class for the common functionality of
    most models on the project."""
    title = models.CharField(max_length=255, default="NOTITLE_ERROR")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creator = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def name(self):
        # name property included as alternative to refactoring large amounts
        # of code expecting a 'name' attribute, and a 'name' makes more
        # sense for the Composer class.
        return self.title

    @name.setter
    def name(self, value):
        self.title = value

    @name.deleter
    def name(self):
        self.title.delete()

    @property
    def uploader(self):
        return self.creator

    @uploader.setter
    def uploader(self, value):
        self.creator = value

    @uploader.deleter
    def uploader(self):
        self.uploader.delete()

    def solr_dict(self):
        """ A method to be over-ridden in children which returns the dict
        of themselves to index in solr.
        """
        raise NotImplementedError

    def solr_index(self, **kwargs):
        """ Delete any duplicates and then index this object in solr.
        :param kwargs:
            commit: True to commit right away. False for batch updates.
        """
        solr_dict = self.solr_dict()
        solr_dict['uuid'] = str(self.uuid)
        if kwargs.get('solrconn'):
            solrconn = kwargs.get('solrconn')
        else:
            solrconn = solr.SolrConnection(settings.SOLR_SERVER)
        solrconn.add(**solr_dict)

        if kwargs.get('commit', True):
            solrconn.commit()

    def solr_delete(self, **kwargs):
        """ Deletes the objects corresponding document in solr.
        :param kwargs:
            commit: True to commit right away. False for batch updates.
        """

        solrconn = solr.SolrConnection(settings.SOLR_SERVER)
        solrconn.delete_query("uuid:{0}".format(str(self.uuid)))

        if kwargs.get('commit', True):
            solrconn.commit()


    def __str__(self):
        return self.title


