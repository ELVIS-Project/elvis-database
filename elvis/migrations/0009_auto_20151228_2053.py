# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0008_auto_20151228_2052'),
    ]

    operations = [
        migrations.AlterField(
                model_name='attachment',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='collection',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='composer',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='genre',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='instrumentvoice',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='language',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='location',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='movement',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='piece',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='source',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
                model_name='tag',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
