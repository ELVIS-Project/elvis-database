from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Comment(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()
    user = models.ForeignKey(User)
    discussion = models.ForeignKey("elvis.Discussion")

    created = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):
        return u"{0}".format(self.text)

    class Meta:
        app_label = "elvis"
