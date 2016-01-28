import datetime
import uuid

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from elvis.models.elvis_model import ElvisModel


class Composer(ElvisModel):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    birth_date = models.IntegerField(blank=True, null=True)
    death_date = models.IntegerField(blank=True, null=True)

    @property
    def piece_count(self):
        return self.pieces.all().count()

    @property
    def movement_count(self):
        return self.movements.all().count()

    @property
    def free_movements(self):
        return self.movements.filter(piece=None)

    @property
    def free_movements_count(self):
        return self.movements.filter(piece=None).count()

    @property
    def cart_id(self):
        return "COM-" + str(self.uuid)

    @property
    def shortened_title(self):
        comma_split = self.title.split(',')
        space_split = self.title.split()
        if len(comma_split) == 1:
            new_name = space_split[0]
        else:
            new_name = comma_split[0]
        space_split = space_split[1:]
        for n in space_split:
            if n[0].isupper():
                new_name += " {0}.".format(n[0])
        return new_name

    def rename(self, new_name):
        """Rename composer and all files associated with it.
        A compose WILL NOT rename files associated with it if you simply
        change its name/title attribute, as there could be thousands of files
        associated with each composer, it would be incredibly inconvenient to
        have to check if all should be renamed every time a composer is saved."""
        self.title = new_name
        self.save()
        for p in self.pieces.all():
            for a in p.attachments.all():
                a.auto_rename()
        for m in self.movements.all():
            for a in m.attachments.all():
                a.auto_rename()

    def solr_dict(self):
        composer = self
        if composer.birth_date:
            birth = datetime.date(composer.birth_date, 1, 1)
        else:
            birth = None
        if composer.death_date:
            death = datetime.date(composer.death_date, 1, 1)
        else:
            death = None

        return {'type': 'elvis_composer',
                'id': int(composer.id),
                'name': composer.name,
                'birth_date': birth,
                'death_date': death,
                'created': composer.created,
                'updated': composer.updated,
                'composers_searchable': composer.name}


@receiver(post_save, sender=Composer)
def save_listener(sender, instance, created, **kwargs):
    instance.solr_index(commit=True)


@receiver(post_delete, sender=Composer)
def delete_listener(sender, instance, **kwargs):
    instance.solr_delete(commit=True)
