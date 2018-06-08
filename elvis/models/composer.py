import datetime

from django.db import models
from elvis.models.elvis_model import ElvisModel


class Composer(ElvisModel):
    class Meta:
        app_label = "elvis"
        ordering = ["title"]

    birth_date = models.IntegerField(blank=True, null=True)
    death_date = models.IntegerField(blank=True, null=True)

    @property
    def piece_count(self):
        return self.pieces.count()

    @property
    def movement_count(self):
        return self.movements.count()

    @property
    def free_movements(self):
        return self.movements.filter(piece=None)

    @property
    def free_movements_count(self):
        return self.movements.filter(piece=None).count()

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
