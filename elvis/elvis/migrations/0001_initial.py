# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
import elvis.models.composer
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name=b'Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                (b'name', models.CharField(max_length=255)),
                (b'description', models.TextField(null=True, blank=True)),
                (b'approved', models.BooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'query', models.CharField(max_length=255)),
                (b'created', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'Composer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                (b'name', models.CharField(max_length=255)),
                (b'birth_date', models.DateField(null=True, blank=True)),
                (b'death_date', models.DateField(null=True, blank=True)),
                (b'picture', models.ImageField(null=True, upload_to=elvis.models.composer.picture_path)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
    ]
