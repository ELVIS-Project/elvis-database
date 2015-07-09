from django.db import models

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import pytz


class Genre(models.Model):
    class Meta:
        ordering = ["name"]
        app_label = "elvis"

    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)



@receiver(post_save, sender=Genre)
def solr_index(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_genre".format(instance.id))
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
            'updated': genre.updated,
            'comment': genre_comment,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Genre)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_genre".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
