import os
import shutil
import random
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime


def upload_path(instance, filename):
    return os.path.join(instance.attachment_path, filename)


class Attachment(models.Model):
    """
        IMPORTANT: This model will store its attachments in a
        random (LM Edit: NOT random - hashed from pk) folder structure. This is to prevent the webapp from
        putting too many files in a single directory.

        The format is:

        attachments/[XX]/[XX]/[PK]

        Where XXXX represents a 2-digit number taken from a subset of the PK
        and [PK] represents the primary key of the attachment padded to 15 zeros.

        This means that you MUST save a blank copy of this model BEFORE
        attempting to attach a file. If not, self.pk will not be set and all
        kinds of weirdness will take place.
    """
    class Meta:
        app_label = "elvis"

    @property
    def attachment_path(self):
        return os.path.join(settings.MEDIA_ROOT,
                            "attachments",
                            "{0:0>2}".format(str(self.pk)[0:2]),
                            "{0:0>2}".format(str(self.pk)[-2:]),
                            "{0:0>15}".format(self.pk))


    old_id = models.IntegerField(null=True, blank=True, db_index=True)
    attachment = models.FileField(upload_to=upload_path, null=True, blank=True, max_length=512)
    source = models.CharField(blank=True, null=True, max_length=200)
    uploader = models.ForeignKey(User, blank=True, null=True, related_name="attachments")
    description = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    @property
    def file_name(self):
        return os.path.basename(self.attachment.name)

    @property
    def attached_to(self):
        p_list = " ".join([p.title for p in self.pieces.all()])
        m_list = " ".join([m.title for m in self.movements.all()])
        return 'm: ' + m_list+ '; p: ' + p_list

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not os.path.exists(self.attachment_path):
            os.makedirs(self.attachment_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.attachment_path):
            shutil.rmtree(self.attachment_path)
        super(Attachment, self).delete(*args, **kwargs)

    def rename(self, new_filename, *args, **kwargs):
        (path, current_name) = os.path.split(self.attachment.name)
        (current_file_name, current_extension) = os.path.splitext(current_name)
        new_filename += current_extension
        new_path = os.path.join(path, new_filename)
        shutil.move(self.attachment.name, new_path)
        self.attachment.name = new_path
        self.save()

    def __unicode__(self):
        return u"{0}".format(self.attachment)
