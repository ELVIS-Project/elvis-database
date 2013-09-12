from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

	def picture_path(self):
		return '/'.join('photos', self.user.__unicode__)

	user = models.ForeignKey(User, unique=True)
	picture = models.ImageField(upload_to=picture_path, null=True)

	def __unicode__(self):
		return u"{0}".format(self.user.username)

	class Meta:
		app_label = "elvis"