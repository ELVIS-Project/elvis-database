import os
import shutil
import random
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime

class Attachment(models.Model):
    """
        IMPORTANT: This model will store its attachments in a
        random folder structure. This is to prevent the webapp from
        putting too many files in a single directory.

        The format is:

        attachments/[XX]/[XX]/[PK]

        Where XXXX represents a 2-digit number taken from a subset of the PK
        and [PK] represents the primary key of the attachment padded to 15 zeros.

        This means that you MUST save a blank copy of this model BEFORE
        attempting to attach a file. If not, self.pk will not be set and all
        kinds of weirdness will take place.
    """

    @property
    def attachment_path(self):
        return os.path.join(settings.MEDIA_ROOT,
                            "attachments",
                            "{0:0>2}".format(str(self.pk)[0:2]),
                            "{0:0>2}".format(str(self.pk)[-2:]),
                            "{0:0>15}".format(self.pk))

    def upload_path(self, filename):
        return os.path.join(self.attachment_path, filename)

    old_id = models.IntegerField(null=True, blank=True, db_index=True)
    attachment = models.FileField(upload_to=upload_path, null=True, max_length=512)
    uploader = models.ForeignKey(User, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # created = models.DateTimeField(default=datetime.now, blank=True)
    # updated = models.DateTimeField(default=datetime.now, blank=True)

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not os.path.exists(self.attachment_path):
            os.makedirs(self.attachment_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.attachment_path):
            shutil.rmtree(self.attachment_path)
        super(Attachment, self).delete(*args, **kwargs)

    def __unicode__(self):
        return u"{0}".format(self.attachment)

    class Meta:
        app_label = "elvis"
