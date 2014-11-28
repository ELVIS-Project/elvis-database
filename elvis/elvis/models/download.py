from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Download(models.Model):
    class Meta:
        app_label = "elvis"

    user = models.ForeignKey(User, blank=True, null=True, related_name="downloads")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, null=True, related_name="downloads")
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0}".format(self.attachments.all())

def create_user_download(sender, instance, created, **kwargs):
    if created:
        Download.objects.create(user=instance)

post_save.connect(create_user_download, sender=User)

