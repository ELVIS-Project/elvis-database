# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0006_auto_20150827_1839'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='discussion',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='first_user',
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='project',
        ),
        migrations.RemoveField(
            model_name='project',
            name='users',
        ),
        migrations.DeleteModel(
            name='Query',
        ),
        migrations.RemoveField(
            model_name='taghierarchy',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='taghierarchy',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='todo',
            name='assigned_to',
        ),
        migrations.RemoveField(
            model_name='todo',
            name='project',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Discussion',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
        migrations.DeleteModel(
            name='TagHierarchy',
        ),
        migrations.DeleteModel(
            name='Todo',
        ),
    ]
