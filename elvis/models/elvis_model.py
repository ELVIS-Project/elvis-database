import solr
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.utils.functional import cached_property


cart_code = {"Piece": "P", "Movement": "M",
             "Collection": "COL", "Composer": "COM"}


class ElvisModel(models.Model):
    """ A super class for the common functionality of
    most models on the project."""
    title = models.CharField(max_length=255, default="NOTITLE_ERROR")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
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

    @cached_property
    def cart_id(self):
        code = cart_code.get(self.__class__.__name__)
        return "{}-{}".format(code, str(self.uuid))

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

    def cache_expire(self):
        cache_levels = ["MIN-", "EMB-", "LIST-"]
        str_uuid = str(self.uuid)
        for prefix in cache_levels:
            cache.delete(prefix + str_uuid)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, **kwargs):
        """Handle attachments, caching, and solr_indexing on save.

        Will expire the cache entry, rename the attachments, and commit
        the changes to solr by default. See kwargs for options.

        :param kwargs:
            -ignore_solr: Do not contact solr in any way.
            -commit_solr: Defaults to true. If False, the changes will
            be sent so solr, but will not be committed (this is much faster
            when doing bulk changes). Otherwise, commit the change.
        """
        self.cache_expire()
        super().save(force_insert, force_update, using, update_fields)

        cls = self.__class__.__name__
        if cls == "Movement":
            # if self.hidden:
            #     self.solr_delete(commit=True);
            for a in self.attachments.all():
                a.auto_rename(**kwargs)

        if cls == "Piece":
            for a in self.attachments.all():
                a.auto_rename(**kwargs)
            for m in self.movements.all():
                m.save(**kwargs)
            # if self.hidden:
            #     self.solr_delete(commit=True);

        if kwargs.get("ignore_solr"):
            pass
        elif kwargs.get("commit_solr", True):
            self.solr_index(commit=True)
        else:
            self.solr_index(commit=False)

    def delete(self, using=None, keep_parents=False, **kwargs):
        """Handle attachments, caching, and solr_indexing on delete.

        Will expire the cache entry, delete the attachments, and commit
        the changes to solr by default. See kwargs for options.

        :param kwargs:
            -ignore_solr: Do not contact solr in any way.
            -commit_solr: Defaults to true. If False, the changes will
            be sent so solr, but will not be committed (this is much faster
            when doing bulk changes). Otherwise, commit the change.
        """
        self.cache_expire()

        cls = self.__class__.__name__
        if cls == "Piece":
            for a in self.attachments.all():
                a.delete(**kwargs)
            for m in self.movements.all():
                m.delete(**kwargs)

        if cls == "Movement":
            for a in self.attachments.all():
                a.delete(**kwargs)

        super().delete(using, keep_parents)

        if kwargs.get("ignore_solr"):
            pass
        elif kwargs.get("commit_solr", True):
            self.solr_delete(commit=True)
        else:
            self.solr_delete(commit=False)

    def __str__(self):
        return self.title

