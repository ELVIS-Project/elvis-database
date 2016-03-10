import os
import shutil

from django.db import models
from django.conf import settings
from elvis.models.elvis_model import ElvisModel
from django.core.files.base import File
import elvis.helpers.name_normalizer as NameNormalizer


def upload_path(instance, filename):
    return os.path.join(instance.attachment_path, filename)


class Attachment(ElvisModel):
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
        ordering = ['id']

    @property
    def attachment_path(self):
        return os.path.join(settings.MEDIA_ROOT,
                            "attachments",
                            "{0:0>2}".format(str(self.pk)[0:2]),
                            "{0:0>2}".format(str(self.pk)[-2:]),
                            "{0:0>15}".format(self.pk))

    attachment = models.FileField(upload_to=upload_path, null=True, blank=True, max_length=512)
    source = models.CharField(blank=True, null=True, max_length=200)

    @property
    def extension(self):
        title, ext = os.path.splitext(self.file_name)
        return ext

    @property
    def file_name(self):
        return os.path.basename(self.attachment.name)

    @property
    def attached_to(self):
        p_list = " ".join([p.title for p in self.pieces.all()])
        m_list = " ".join([m.title for m in self.movements.all()])
        return 'm: ' + m_list + '; p: ' + p_list

    @property
    def url(self):
        url = os.path.join(settings.MEDIA_URL, str(self.attachment.name))
        return url

    def solr_dict(self):
        return {}

    def solr_index(self, **kwargs):
        pass

    def solr_delete(self, **kwargs):
        pass

    def attach_file(self, file_path, file_name, parent, **kwargs):
        i = kwargs.get('number', None)
        i = str(i) if i else ""
        source = kwargs.get('source', None)

        new_name = "{0}_{1}_{2}.{3}".format(NameNormalizer.sanitize_name(parent.title.strip()),
                                            NameNormalizer.sanitize_name(parent.composer.name.strip()),
                                            "file" + str(i),
                                            file_name.rsplit('.')[-1])
        #replace unicode in string with normalized chars
        new_name = self.normalize_name(new_name)

        old_path = os.path.join(file_path, file_name)
        new_path = os.path.join(file_path, new_name)
        os.rename(old_path, new_path)

        if source:
            self.source = source

        with open(new_path, 'rb+') as dest:
            file_content = File(dest)
            self.attachment.save(new_name, file_content)

        splt = self.attachment.name.split('attachments')
        self.attachment.name = "attachments" + splt[-1]

        self.title = self.file_name
        self.save()

    def delete(self, *args, **kwargs):
        if os.path.exists(self.attachment_path):
            shutil.rmtree(self.attachment_path)
        super(Attachment, self).delete(*args, **kwargs)

    def auto_rename(self, **kwargs):
        """Determine the correct name for the file, then rename it if necessary"""
        parent = None
        if self.pieces.all():
            parent = self.pieces.first()
            parent_str = parent.title.strip()
        elif self.movements.all():
            parent = self.movements.first()
            mov = parent
            if mov.piece:
                piece_str = mov.piece.title.strip()
                parent_str = piece_str + "_" + mov.title.strip()
            else:
                parent_str = mov.title.strip()
        else:
            print("{0} is an orphan and will be deleted".format(self.title))
            self.delete()
            return

        # Find position in parent attachments for an index in the name.
        i = 1
        for a in parent.attachments.all():
            if a == self:
                break
            else:
                i += 1

        # Find current file extension.
        old_path = os.path.join(settings.MEDIA_ROOT, self.attachment.name)
        (path, current_name) = os.path.split(old_path)
        (current_file_name, current_extension) = os.path.splitext(current_name)

        new_name = "{0}_{1}_{2}{3}".format(NameNormalizer.sanitize_name(parent_str),
                                           NameNormalizer.sanitize_name(parent.composer.name.strip()),
                                           "file" + str(i),
                                           current_extension)
        new_name = self.normalize_name(new_name)
        new_path = os.path.join(path, new_name)

        # Return now if there's no work to do.
        if self.file_name == new_name:
            return

        shutil.move(old_path, new_path)

        # Point the attachment to the new file
        old_rel_path, old_name = os.path.split(self.attachment.name)
        self.attachment.name = os.path.join(old_rel_path, new_name)
        self.save(**kwargs)
        return

    def __unicode__(self):
        return "{0}".format(self.attachment)

    def normalize_name(self, name):
        return NameNormalizer.normalize_name(name)