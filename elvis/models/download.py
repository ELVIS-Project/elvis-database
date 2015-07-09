from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Download(models.Model):
    class Meta:
        app_label = "elvis"

    user = models.ForeignKey(User, blank=True, null=True, related_name="downloads")
    collection_pieces = models.ManyToManyField("elvis.Piece", blank=True)
    collection_movements = models.ManyToManyField("elvis.Movement", blank=True)
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, related_name="downloads")
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0}".format(self.attachments.all())

    @property
    def cart_size(self):
        count = self.collection_pieces.all().count() + self.collection_movements.all().count()
        for piece in self.collection_pieces.all():
            count += piece.movements.all().count()
        return count


def create_user_download(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return False
    if created:
        Download.objects.create(user=instance)

post_save.connect(create_user_download, sender=User)

