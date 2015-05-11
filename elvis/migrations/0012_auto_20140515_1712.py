# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0011_todo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='approved',
            field=models.NullBooleanField(),
        ),
    ]
