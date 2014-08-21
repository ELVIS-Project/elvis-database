import os
from django.db import models
from django.contrib.auth.models import User

def picture_path(instance, filename):
    return os.path.join('user_photos', filename)

class UserProfile(models.Model):

    user = models.ForeignKey(User, unique=True)
    picture = models.ImageField(upload_to=picture_path, null=True, blank=True)
    #location = models.CharField(max_length=140) 
    #affiliation = models.CharField(max_length=300)

    def __unicode__(self):
        return u"{0}".format(self.user.username)

    class Meta:
        app_label = "elvis"

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])