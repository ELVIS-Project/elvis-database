# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0004_auto_20150814_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalcomposer',
            name='history_user',
        ),
        migrations.DeleteModel(
            name='HistoricalComposer',
        ),
    ]
