# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0009_auto_20150828_1955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='composer',
            name='old_birth_date',
        ),
        migrations.RemoveField(
            model_name='composer',
            name='old_death_date',
        ),
        migrations.RemoveField(
            model_name='movement',
            name='old_date_of_composition',
        ),
        migrations.RemoveField(
            model_name='movement',
            name='old_date_of_composition2',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='old_date_of_composition',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='old_date_of_composition2',
        ),
    ]
