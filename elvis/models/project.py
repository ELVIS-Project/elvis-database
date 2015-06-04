from django.db import models

#django signal handlers
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField("elvis.UserProfile", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = "elvis"


@receiver(post_save, sender=Project)
def solr_index(sender, instance, created, **kwargs):
    import uuid
    from django.conf import settings
    import solr

    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_project".format(instance.id))
    if record:
        solrconn.delete(record.results[0]['id'])
    
    project = instance
    d = {
            'type': 'elvis_project',
            'id': str(uuid.uuid4()),
            'item_id': int(project.id),
            'name': project.name,
            'description': project.description,
            'created': project.created,
            'updated': project.updated,
    }
    solrconn.add(**d)
    solrconn.commit()


@receiver(post_delete, sender=Project)
def solr_delete(sender, instance, **kwargs):
    from django.conf import settings
    import solr
    solrconn = solr.SolrConnection(settings.SOLR_SERVER)
    record = solrconn.query("item_id:{0} AND type:elvis_project".format(instance.id))
    if record:
        # the record already exists, so we'll remove it.
        solrconn.delete(record.results[0]['id'])
        solrconn.commit()