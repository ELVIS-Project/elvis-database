# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0010_auto_20150828_2010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attachment',
            old_name='file',
            new_name='attachment',
        ),
        migrations.RenameField(
            model_name='attachment',
            old_name='creator',
            new_name='uploader',
        ),
        migrations.AddField(
            model_name='attachment',
            name='description',
            field=models.CharField(null=True, max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='old_id',
            field=models.IntegerField(null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='old_id',
            field=models.IntegerField(null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='composer',
            name='old_birth_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='composer',
            name='old_death_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='composer',
            name='old_id',
            field=models.IntegerField(null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='old_date_of_composition',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='old_date_of_composition2',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='old_id',
            field=models.IntegerField(null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='old_date_of_composition',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='old_date_of_composition2',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='old_id',
            field=models.IntegerField(null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='old_id',
            field=models.IntegerField(null=True, blank=True, db_index=True),
        ),
    ]
