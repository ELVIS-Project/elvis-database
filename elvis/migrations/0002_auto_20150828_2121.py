# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='composer',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='instrumentvoice',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='source',
            options={'ordering': ['title']},
        ),
        migrations.RenameField(
            model_name='composer',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='genre',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='instrumentvoice',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='language',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='source',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='name',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='composer',
            name='old_birth_date',
        ),
        migrations.RemoveField(
            model_name='composer',
            name='old_death_date',
        ),
        migrations.RemoveField(
            model_name='composer',
            name='old_id',
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
            model_name='movement',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='old_date_of_composition',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='old_date_of_composition2',
        ),
        migrations.RemoveField(
            model_name='piece',
            name='old_id',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='old_id',
        ),
    ]
