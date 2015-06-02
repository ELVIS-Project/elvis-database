from django.db import models
from django.contrib.auth.models import User

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

class Discussion(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey("elvis.Project")
    first_comment = models.TextField()
    first_user = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = "elvis"


@receiver(post_save, sender=Discussion)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0}".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])

    discussion = instance
    d = {
            'type': 'elvis_discussion',
            'id': str(uuid.uuid4()),
            'item_id': int(discussion.id),
            'name': discussion.name,
            'comment_text': discussion.text,
            'created': discussion.created,
            'updated': discussion.updated,
            'parent_project_name': discussion.project.name,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Discussion)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0}".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()
        