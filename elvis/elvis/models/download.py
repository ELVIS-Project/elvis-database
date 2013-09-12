from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

class Download(models.Model):
	user = models.ForeignKey(User, blank=True, null=True)
	attachment = models.ForeignKey("elvis.Attachment", blank=True, null=True)

	saved = models.DateTimeField(default=datetime.now, blank=True)

	def __unicode__(self):
		return self.attachment.__unicode__

	class Meta:
		app_label = "elvis"
