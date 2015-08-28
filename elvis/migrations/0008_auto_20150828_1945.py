# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0007_auto_20150828_1412'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attachment',
            old_name='uploader',
            new_name='creator',
        ),
        migrations.RenameField(
            model_name='attachment',
            old_name='attachment',
            new_name='file',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='description',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='old_id',
        ),
    ]
