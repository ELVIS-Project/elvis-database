# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0004_auto_20150901_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='uploader',
        ),
        migrations.RemoveField(
            model_name='movement',
            name='uploader',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='uploader',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='description',
        ),
    ]
