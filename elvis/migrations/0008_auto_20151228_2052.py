# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('elvis', 'Attachment')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Collection')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Composer')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Genre')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'InstrumentVoice')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Language')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Location')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Movement')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Piece')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Source')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()
    MyModel = apps.get_model('elvis', 'Tag')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0007_auto_20151228_2051'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
