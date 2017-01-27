import os
import shutil

from django.db import models
from django.conf import settings
from elvis.models.elvis_model import ElvisModel
from django.core.files.base import File
import elvis.helpers.name_normalizer as NameNormalizer


def upload_path(instance, filename):
    """Calculate the path an attachment will be initially saved at.

    Implementation Note: This function exists outside the Attachment model
    but takes an Attachment as the `instance` argument. This is because this
    function computes the default file path for any new attachment, but it must
    use the `pk` of the instantiated attachment to compute this value. That is,
    this allows us to define the class-default as being dependent on an instance
    attribute.
    """
    return os.path.join(instance.compute_absolute_file_dir(), filename)


class ParentResolveError(Exception):
    """Exception raised when an Attachment's parent can not be resolved."""
    pass


class RenameError(Exception):
    """Exception raised when an Attachment's parent can not be resolved."""
    pass


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

    attachment = models.FileField(upload_to=upload_path, null=True, blank=True, max_length=512)
    source = models.CharField(blank=True, null=True, max_length=200)

    def __str__(self):
        return self.file_name

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

    @property
    def parent(self):
        """The Piece or Movement this Attachment is attached to."""
        pieces = self.pieces.all()
        movements = self.movements.all()
        p_len = len(pieces)
        m_len = len(movements)

        # Handle multiple attachments.
        if p_len >= 1 and m_len >= 1:
            raise ParentResolveError("Attached to at least one Piece and Movement.")
        if p_len > 1 or m_len > 1:
            problem_model = 'Piece' if p_len > 1 else 'Movement'
            raise ParentResolveError("Attached to more than 1 {}.".format(problem_model))

        # Return valid values.
        if p_len == 1:
            return pieces[0]
        if m_len == 1:
            return movements[0]

        # Or report error.
        raise ParentResolveError("Attachment has no parent.")

    def solr_dict(self):
        return {}

    def solr_index(self, **kwargs):
        pass

    def solr_delete(self, **kwargs):
        pass

    # TODO: roll this functionality into a proper instantiation procedure.
    def attach_file(self, file_path, file_name, position, source=None):
        """Attaches a file to this attachment.

        Assumes that this Attachment object already has a parent, and
        that this parent has a composer. Given this, it is best to create
        attachments at the end of a piece-creating workflow.

         Args:
            file_path (str): The path up to the dir where this file is held.
            file_name (str): The name of this file.
            position (int): The index of this file in its parents list of files.
            source (str): The source of the attached file.
        """

        # Compute the new name for the file and move it to its correct position.
        new_name = self.compute_correct_file_name(position=position,
                                                  extension="." + file_name.rsplit('.')[-1])
        old_path = os.path.join(file_path, file_name)
        new_path = os.path.join(self.compute_absolute_file_dir(), new_name)
        if not os.path.exists(self.compute_absolute_file_dir()):
            os.makedirs(self.compute_absolute_file_dir())

        if source:
            self.source = source

        # Attach the file to the attachment object. Since we pass in the new_path,
        # it will copy the file there. Then, delete the old file.
        with open(old_path, 'rb+') as dest:
            file_content = File(dest)
            self.attachment.save(new_path, file_content)
        os.remove(old_path)

        # Save the relative directory of the new file as the attachment name.
        splt = self.attachment.name.split('attachments')
        self.attachment.name = "attachments" + splt[-1]

        # Update this Attachments title with the files name.
        self.title = new_name
        self.save()

    def delete(self, *args, **kwargs):
        abs_path = self.compute_absolute_path()
        if os.path.exists(abs_path):
            os.remove(abs_path)
        super(Attachment, self).delete(*args, **kwargs)

    # TODO Remove this function once correct naming is guaranteed by instantiation.
    def auto_rename(self, **kwargs):
        """Automatically rename the file to correct representation."""
        old_path = os.path.join(settings.MEDIA_ROOT, self.attachment.name)
        new_path = self.compute_absolute_path()
        shutil.move(old_path, new_path)

        # Point the attachment to the new file
        self.attachment.name = self.compute_relative_path()
        self.save(**kwargs)
        return

    def get_index_from_parent(self):
        """Determine which position this attachment has in it's parent's list
        of attachments.

        Returns: An int, or raises a ParentResolveError.
        """
        parent = self.parent
        for position, a in enumerate(parent.attachments.all()):
            if a.pk == self.pk:
                return position + 1
        raise ParentResolveError("Could not find self in parent's attachments.")

    def compute_relative_file_dir(self):
        """Generate the relative directory the attached file resides in.

        Note: This function COMPUTES its result. It is not based on the ACTUAL properties
        of some file. That is, you should use this function to compute the properties of
        a file you need to place/name, NOT to get information about the actual file linked
        to by this Attachment. It is a prescriptive, not descriptive result. Examine the
        properties of the Attachment.attachment object for the actual properties of the
        real file.
        """
        return os.path.join("attachments",
                            "{0:0>2}".format(str(self.pk)[0:2]),
                            "{0:0>2}".format(str(self.pk)[-2:]),
                            "{0:0>15}".format(self.pk))

    def compute_absolute_file_dir(self):
        """Generate the absolute directory the attached file should reside in.

        Note: This function COMPUTES its result. It is not based on the ACTUAL properties
        of some file. That is, you should use this function to compute the properties of
        a file you need to place/name, NOT to get information about the actual file linked
        to by this Attachment. It is a prescriptive, not descriptive result. Examine the
        properties of the Attachment.attachment object for the actual properties of the
        real file.
        """
        return os.path.join(settings.MEDIA_ROOT, self.compute_relative_file_dir())

    def compute_correct_file_name(self, position=None, extension=None):
        """Generate the name the file should take on disk, given metadata.

        Note 1: If a new Attachment is being created you must provide the position
        and extension arguments. Otherwise, this function expects this information
        is already available in the Attachment instance.

        Note 2: This function COMPUTES its result. It is not based on the ACTUAL properties
        of some file. That is, you should use this function to compute the properties of
        a file you need to place/name, NOT to get information about the actual file linked
        to by this Attachment. It is a prescriptive, not descriptive result. Examine the
        properties of the Attachment.attachment object for the actual properties of the
        real file.

        Args:
            position (int): The index of this Attachment's in its parent's list of files.
            extension (str): The file extension with dot included (e.g. '.midi, '.exe')

        Returns: A string with the file name the file should be saved with on disk.
        """
        # Generate a parent_str which contains piece and movement names.
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
            msg = 'Attachment "{0}" is an orphan and should be deleted'
            raise ParentResolveError(msg.format(self.title))

        # Generate file name.
        position = str(position) if position else self.get_index_from_parent()
        extension = extension if extension else self.extension
        new_name = "{0}_{1}_{2}{3}".format(NameNormalizer.sanitize_name(parent_str),
                                           NameNormalizer.sanitize_name(parent.composer.name.strip()),
                                           "file" + str(position), extension)
        return NameNormalizer.normalize_name(new_name)

    def compute_relative_path(self):
        """Generate the relative path this file should take with respect to metadata.

        Note: This function COMPUTES its result. It is not based on the ACTUAL properties
        of some file. That is, you should use this function to compute the properties of
        a file you need to place/name, NOT to get information about the actual file linked
        to by this Attachment. It is a prescriptive, not descriptive result. Examine the
        properties of the Attachment.attachment object for the actual properties of the
        real file.

        Returns: A string containing the relative path where this file SHOULD be saved.
            Note, this path is relative to settings.MEDIA_ROOT.
        """
        file_name = self.compute_correct_file_name()
        path = self.compute_relative_file_dir()
        return os.path.join(path, file_name)

    def compute_absolute_path(self):
        """Generate the absolute path this file should take with respect to metadata.

        Note: This function COMPUTES its result. It is not based on the ACTUAL properties
        of some file. That is, you should use this function to compute the properties of
        a file you need to place/name, NOT to get information about the actual file linked
        to by this Attachment. It is a prescriptive, not descriptive result. Examine the
        properties of the Attachment.attachment object for the actual properties of the
        real file.

        Returns: A string containing the absolute path where this file SHOULD be saved.
        """
        file_name = self.compute_correct_file_name()
        path = self.compute_absolute_file_dir()
        return os.path.join(path, file_name)
