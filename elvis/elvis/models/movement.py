from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


class Movement(models.Model):
    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True)
    piece = models.ForeignKey("elvis.Piece", blank=True, null=True)
    corpus = models.ForeignKey("elvis.Corpus", blank=True, null=True)
    composer = models.ForeignKey("elvis.Composer", blank=True, null=True)
    date_of_composition = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True)
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    number_of_queries = models.IntegerField(blank=True, null=True)
    number_of_downloads = models.IntegerField(blank=True, null=True)

    #created = models.DateTimeField(auto_now_add=True)
    #updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    updated = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):
        return u"{0}".format(self.title)

    class Meta:
        app_label = "elvis"
