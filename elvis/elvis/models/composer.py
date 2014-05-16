import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

def picture_path(instance, filename):
    return os.path.join("photos", "composers", filename)


class Composer(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["name"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    picture = models.ImageField(upload_to=picture_path, null=True)
    # number_of_queries = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)


@receiver(post_save, sender=Composer)
def solr_index(sender, instance, created, **kwargs):
    import uuid  #unique id
    from django.conf import settings 
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)   # connect to solr server
    record = solrconn.query("type:elvis_composer item_id:{0}".format(instance.id)) # search for any previous entries of instance
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    # take instance, build dictionary around instance && use shorthand ** to add to solr
    composer = instance
    #print(composer.name)
    d = {
            'type': 'elvis_composer',
            'id': str(uuid.uuid4()),
            'item_id': int(composer.id), # called composer_id in elvis/solr_index.py 
            'composer_name': composer.name,
            'composer_birth': composer.birth_date,
            'composer_death': composer.death_date,
            'created': composer.created,
            'updated': composer.updated,
    }
    solrconn.add(**d) 
    solrconn.commit() # update based on previous dictionary


@receiver(post_delete, sender=Composer)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_composer item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])