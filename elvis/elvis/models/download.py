from django.db import models
from django.contrib.auth.models import User

class Download(models.Model):
    class Meta:
        app_label = "elvis"

    user = models.ForeignKey(User, blank=True, null=True, related_name="downloads")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="downloads")

    def __unicode__(self):
        return u"{0}".format(self.attachments)
