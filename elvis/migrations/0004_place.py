# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0003_attachment_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('elvis.location',),
        ),
    ]
