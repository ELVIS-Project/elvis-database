from django.db import models

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from datetime import datetime
import pytz

class Genre(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)



@receiver(post_save, sender=Genre)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it first.
        solrconn.delete(record.results[0]['id'])

    genre = instance

    #LM: Same ugly bit of code as in all the models, remove when encoding issues are fixed.
    try:
        genre_name = unicode(genre.name)
    except UnicodeDecodeError:
        genre_name = genre.name.decode('utf-8')


    if genre.comment is None:
        genre_comment = None
    else:
        try:
            genre_comment = unicode(genre.comment)
        except UnicodeDecodeError:
            genre_comment = genre.comment.decode('utf-8')
            
    try:
        genre_created = pytz.utc.localize(genre.created)
    except ValueError:
        genre_created = genre.created


    d = {
            'type': 'elvis_genre',
            'id': str(uuid.uuid4()),
            'item_id': int(genre.id),
            'name': genre_name,
            'genres_searchable': genre_name,
            'genres': genre_name,
            'created': genre_created,
            'updated': datetime.now(pytz.utc),
            'comment': genre_comment,
    }
    # Only commits the change if the file is more than a minute old. This is to prevent repeated commits and dictionary
    # rebuilding on the solr server during piece creation.
    c = datetime.now(pytz.utc) - genre.created
    c = divmod(c.days * 86400 + c.seconds, 60)
    if c[0] > 1:
        solrconn.commit()


@receiver(post_delete, sender=Genre)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
        