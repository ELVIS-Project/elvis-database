from django.db import models
from django.contrib.auth.models import User

class ElvisModel(models.Model):
    title = models.CharField(max_length=255, default="NOTITLE_ERROR")
    creator = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def name(self):
        # name property included as alternative to refactoring large amounts
        # of code expecting a 'name' attribute, and a 'name' makes more
        # sense for the Composer class.
        return self.title

    @name.setter
    def name(self, value):
        self.title = value

    @name.deleter
    def name(self):
        self.title.delete()

    def __str__(self):
        return self.title


