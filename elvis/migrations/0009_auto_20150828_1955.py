# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0008_auto_20150828_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='composer',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='movement',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='description',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='old_id',
        ),
    ]
