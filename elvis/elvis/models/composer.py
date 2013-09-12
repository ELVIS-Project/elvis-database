from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Composer(models.Model):

    def picture_path(self):
        return '/'.join('photos/composers', self.name.__unicode__)

    old_id = models.IntegerField(db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    picture = models.ImageField(upload_to=picture_path, null=True)
    number_of_queries = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # created = models.DateTimeField(default=datetime.now, blank=True)
    # updated = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = "elvis"
