from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

class UserProfile(models.Model):
    """Extension of default User model with extra information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    accepted_tos = models.BooleanField(default=False)

    @property
    def username(self):
        return self.user.username

    def __repr__(self):
        return "<UserProfile: {}>".format(self.username)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)