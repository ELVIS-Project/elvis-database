from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


class Movement(models.Model):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="movements")
    piece = models.ForeignKey("elvis.Piece", blank=True, null=True, related_name="movements")
    corpus = models.ForeignKey("elvis.Corpus", blank=True, null=True, related_name="movements")
    composer = models.ForeignKey("elvis.Composer", blank=True, null=True, related_name="movements")
    date_of_composition = models.DateField(blank=True, null=True)
    number_of_voices = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField("elvis.Tag", blank=True, null=True)
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="movements")
    comment = models.TextField(blank=True, null=True)

    # number_of_queries = models.IntegerField(blank=True, null=True)
    # number_of_downloads = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.title)