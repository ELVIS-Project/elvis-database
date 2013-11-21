import os
from django.db import models
from datetime import datetime
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

class Composer(models.Model):

    def picture_path(self, filename):
        return os.path.join("photos", "composers", filename)

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    picture = models.ImageField(upload_to=picture_path, null=True)
    number_of_queries = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = "elvis"

@receiver(post_save, sender=Composer)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_composer item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    composer = instance
    print(composer.name)
    d = {
        'type': 'elvis_composer',
        'id': str(uuid.uuid4()),
        'item_id': int(composer.id),
        'composer_name': unicode(composer.name),
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Composer)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_composer item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])