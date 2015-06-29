# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0005_auto_20150605_2048'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='collection_movements',
            field=models.ManyToManyField(to='elvis.Movement', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='collection_pieces',
            field=models.ManyToManyField(to='elvis.Piece', null=True, blank=True),
        ),
    ]
