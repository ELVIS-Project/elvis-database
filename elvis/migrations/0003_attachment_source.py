# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0002_auto_20150529_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='source',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
