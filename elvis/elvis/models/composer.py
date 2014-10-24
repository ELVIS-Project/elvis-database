import os, pytz
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from django.conf import settings

def picture_path(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, "pictures", "composers", filename)


class Composer(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["name"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    # LM: I suspect this is because of the new django beta, but image fields require blank=True to be optional; else it is required in admin
    picture = models.ImageField(upload_to=picture_path, null=True, blank=True)

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

    # Remove between here...
    try:
        composer_name = unicode(composer.name)
    except UnicodeDecodeError:
        composer_name = composer.name.decode('utf-8')

    if composer.birth_date is None:
        composer_birth_date = None
    else:
        try:
        # IMPORTANT: For drupal dumping purposes, insert pytz.utc.localize(composer.birth_date) in RHS of assignment
        # ELSE, stick with just composer.birth_date
            composer_birth_date = pytz.utc.localize(composer.birth_date)
        except AttributeError:
           composer_birth_date = composer.birth_date

    if composer.death_date is None:
        composer_death_date = None
    else:
        try:
        # IMPORTANT, see composer_birth_date assignment.
            composer_death_date = pytz.utc.localize(composer.death_date)
        except AttributeError:
           composer_death_date = composer.death_date
    # ... and here after encoding issues are fixed

    d = {
            'type': 'elvis_composer',
            'id': str(uuid.uuid4()),
            'item_id': int(composer.id), # called composer_id in elvis/solr_index.py 
            'composer_name': composer_name,
            'birth_date': composer_birth_date,
            'death_date': composer_death_date,
            'created': composer.created,
            'updated': composer.updated,
    }
    solrconn.add(**d) 
    solrconn.commit() # update based on previous dictionary

    #Update solr & attachments for all composed pieces/movements -- by resaving each piece/movement


@receiver(post_delete, sender=Composer)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("type:elvis_composer item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
