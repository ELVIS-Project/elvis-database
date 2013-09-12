from django.db import models
from django.contrib.auth.models import User


class Corpus(models.Model):

    def picture_path(self):
        return '/'.join('photos/corpora', self.title.__unicode__)

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    creator = models.ForeignKey(User)
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    number_of_queries = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # created = models.DateTimeField(default=datetime.now, blank=True)
    # updated = models.DateTimeField(default=datetime.now, blank=True)

    picture = models.ImageField(upload_to=picture_path, null=True)

    def __unicode__(self):
        return u"{0}".format(self.title)

    class Meta:
        verbose_name_plural = "corpora"
        app_label = "elvis"
