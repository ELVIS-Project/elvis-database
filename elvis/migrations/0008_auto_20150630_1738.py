# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0007_auto_20150626_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='movement',
            name='vocalization',
            field=models.CharField(default=b'Unknown', max_length=50),
        ),
        migrations.AddField(
            model_name='piece',
            name='vocalization',
            field=models.CharField(default=b'Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='movement',
            name='religiosity',
            field=models.CharField(default=b'Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='piece',
            name='religiosity',
            field=models.CharField(default=b'Unknown', max_length=50),
        ),
    ]
