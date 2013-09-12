from django.db import models
from django.contrib.auth.models import User


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
