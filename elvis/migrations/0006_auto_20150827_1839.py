# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0005_auto_20150819_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movement',
            name='religiosity',
            field=models.CharField(default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='movement',
            name='vocalization',
            field=models.CharField(default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='piece',
            name='religiosity',
            field=models.CharField(default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='piece',
            name='vocalization',
            field=models.CharField(default='Unknown', max_length=50),
        ),
    ]
