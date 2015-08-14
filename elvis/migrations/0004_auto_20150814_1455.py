# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0003_auto_20150805_1954'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movement',
            old_name='date_of_composition2',
            new_name='composition_end_date',
        ),
        migrations.RenameField(
            model_name='movement',
            old_name='date_of_composition',
            new_name='composition_start_date',
        ),
        migrations.RenameField(
            model_name='piece',
            old_name='date_of_composition2',
            new_name='composition_end_date',
        ),
        migrations.RenameField(
            model_name='piece',
            old_name='date_of_composition',
            new_name='composition_start_date',
        ),
    ]
