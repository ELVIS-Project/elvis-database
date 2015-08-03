import os
from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import datetime

def picture_path(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, "pictures", "composers", filename)

class Composer(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["name"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    old_birth_date = models.DateField(blank=True, null=True)
    old_death_date = models.DateField(blank=True, null=True)
    birth_date = models.IntegerField(blank=True, null=True)
    death_date = models.IntegerField(blank=True, null=True)
    history = HistoricalRecords()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    @property
    def piece_count(self):
        return self.pieces.all().count()

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def free_movements(self):
        return self.movements.filter(piece=None)

    @property
    def free_movements_count(self):
        return self.movements.filter(piece=None).count()

@receiver(post_save, sender=Composer)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False

    import uuid
    import solr
    from django.conf import settings 

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_composer".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    composer = instance
    d = {'type': 'elvis_composer',
         'id': str(uuid.uuid4()),
         'item_id': int(composer.id),
         'name': composer.name,
         'birth_date': datetime.date(composer.birth_date, 01, 01),
         'death_date': datetime.date(composer.death_date, 01, 01),
         'created': composer.created,
         'updated': composer.updated,
         'composers_searchable': composer.name}
    solrconn.add(**d)
    solrconn.commit()

@receiver(post_delete, sender=Composer)
def solr_delete(sender, instance, **kwargs):
    import solr
    from django.conf import settings

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_composer".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
