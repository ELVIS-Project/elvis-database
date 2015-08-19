import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class UserProfile(models.Model):

    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
    #location = models.CharField(max_length=140)
    #affiliation = models.CharField(max_length=300)
    #TODO: Queries, Contributions, Collections

    def __unicode__(self):
        return u"{0}".format(self.user.username)

    class Meta:
        app_label = "elvis"

def create_user_profile(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])