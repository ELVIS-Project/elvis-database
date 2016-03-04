import datetime

from django.db import models
from elvis.models.elvis_model import ElvisModel


class AbstractComposition(ElvisModel):
    class Meta:
        abstract = True

    # Relationships
    collections = models.ManyToManyField("elvis.Collection", blank=True, related_name="%(class)ss")
    composer = models.ForeignKey("elvis.Composer", db_index=True, blank=True, null=True, related_name="%(class)ss")
    genres = models.ManyToManyField("elvis.Genre", blank=True, related_name="%(class)ss")
    instruments_voices = models.ManyToManyField("elvis.InstrumentVoice", blank=True, related_name="%(class)ss")
    languages = models.ManyToManyField("elvis.Language", blank=True, related_name="%(class)ss")
    locations = models.ManyToManyField("elvis.Location", blank=True, related_name="%(class)ss")
    sources = models.ManyToManyField("elvis.Source", blank=True, related_name="%(class)ss")
    attachments = models.ManyToManyField("elvis.Attachment", blank=True, related_name="%(class)ss")
    tags = models.ManyToManyField("elvis.Tag", blank=True, related_name="%(class)ss")

    # Normal Fields
    number_of_voices = models.IntegerField(blank=True, null=True)
    religiosity = models.CharField(max_length=50, default="Unknown")
    vocalization = models.CharField(max_length=50, default="Unknown")
    composition_start_date = models.IntegerField(blank=True, null=True)
    composition_end_date = models.IntegerField(blank=True, null=True)

    @property
    def file_formats(self):
        format_list = []
        for att in self.attachments.all():
            ext = att.extension
            if ext not in format_list:
                format_list.append(ext)
        return format_list

    @property
    def tagged_as(self):
        return " ".join([t.name for t in self.tags.all()])

    def solr_dict(self):
        raise NotImplementedError
