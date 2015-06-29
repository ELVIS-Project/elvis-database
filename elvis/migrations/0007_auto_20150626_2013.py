# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0006_auto_20150608_1938'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movement',
            options={'ordering': ['position', 'title']},
        ),
        migrations.AddField(
            model_name='movement',
            name='religiosity',
            field=models.CharField(default=b'Unknown', max_length=255),
        ),
        migrations.AddField(
            model_name='piece',
            name='religiosity',
            field=models.CharField(default=b'Unknown', max_length=255),
        ),
        migrations.AlterField(
            model_name='movement',
            name='tags',
            field=models.ManyToManyField(related_name='movements', null=True, to='elvis.Tag', blank=True),
        ),
    ]
