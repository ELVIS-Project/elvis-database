# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movement',
            options={'ordering': ['position']},
        ),
        migrations.AddField(
            model_name='movement',
            name='position',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
