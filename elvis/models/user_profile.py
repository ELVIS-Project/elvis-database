from django.contrib.auth.models import User
from django.db import models


# TODO: Fix it so a UserProfile is generated with each new user.
class UserProfile(models.Model):
    """Extension of default User model with extra information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    accepted_tos = models.BooleanField(default=False)

    @property
    def username(self):
        return self.user.username

    def __repr__(self):
        return "<UserProfile: {}>".format(self.username)
