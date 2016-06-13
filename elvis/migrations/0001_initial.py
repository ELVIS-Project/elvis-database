# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import elvis.models.attachment
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('old_id', models.IntegerField(null=True, db_index=True, blank=True)),
                ('attachment', models.FileField(max_length=512, null=True, upload_to=elvis.models.attachment.upload_path, blank=True)),
                ('source', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('uploader', models.ForeignKey(related_name='attachments', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('public', models.NullBooleanField()),
                ('old_id', models.IntegerField(null=True, db_index=True, blank=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name_plural': 'collections',
            },
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('old_id', models.IntegerField(null=True, db_index=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('old_birth_date', models.DateField(null=True, blank=True)),
                ('old_death_date', models.DateField(null=True, blank=True)),
                ('birth_date', models.IntegerField(null=True, blank=True)),
                ('death_date', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('attachments', models.ManyToManyField(related_name='downloads', to='elvis.Attachment', blank=True)),
                ('collection_collections', models.ManyToManyField(related_name='user_downloads', to='elvis.Collection', blank=True)),
                ('collection_composers', models.ManyToManyField(related_name='user_downloads', to='elvis.Composer', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='InstrumentVoice',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Movement',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('old_id', models.IntegerField(null=True, db_index=True, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('position', models.IntegerField(null=True, blank=True)),
                ('old_date_of_composition', models.DateField(null=True, blank=True)),
                ('old_date_of_composition2', models.DateField(null=True, blank=True)),
                ('composition_start_date', models.IntegerField(null=True, blank=True)),
                ('composition_end_date', models.IntegerField(null=True, blank=True)),
                ('number_of_voices', models.IntegerField(null=True, blank=True)),
                ('religiosity', models.CharField(max_length=50, default='Unknown')),
                ('vocalization', models.CharField(max_length=50, default='Unknown')),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attachments', models.ManyToManyField(related_name='movements', to='elvis.Attachment', blank=True)),
                ('collections', models.ManyToManyField(related_name='movements', to='elvis.Collection', blank=True)),
                ('composer', models.ForeignKey(related_name='movements', null=True, to='elvis.Composer', blank=True)),
                ('genres', models.ManyToManyField(related_name='movements', to='elvis.Genre', blank=True)),
                ('instruments_voices', models.ManyToManyField(related_name='movements', to='elvis.InstrumentVoice', blank=True)),
                ('languages', models.ManyToManyField(related_name='movements', to='elvis.Language', blank=True)),
                ('locations', models.ManyToManyField(related_name='movements', to='elvis.Location', blank=True)),
            ],
            options={
                'ordering': ['position', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('old_id', models.IntegerField(null=True, db_index=True, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('old_date_of_composition', models.DateField(null=True, blank=True)),
                ('old_date_of_composition2', models.DateField(null=True, blank=True)),
                ('composition_start_date', models.IntegerField(null=True, blank=True)),
                ('composition_end_date', models.IntegerField(null=True, blank=True)),
                ('number_of_voices', models.IntegerField(null=True, blank=True)),
                ('religiosity', models.CharField(max_length=50, default='Unknown')),
                ('vocalization', models.CharField(max_length=50, default='Unknown')),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attachments', models.ManyToManyField(related_name='pieces', to='elvis.Attachment', blank=True)),
                ('collections', models.ManyToManyField(related_name='pieces', to='elvis.Collection', blank=True)),
                ('composer', models.ForeignKey(related_name='pieces', null=True, to='elvis.Composer', blank=True)),
                ('genres', models.ManyToManyField(related_name='pieces', to='elvis.Genre', blank=True)),
                ('instruments_voices', models.ManyToManyField(related_name='pieces', to='elvis.InstrumentVoice', blank=True)),
                ('languages', models.ManyToManyField(related_name='pieces', to='elvis.Language', blank=True)),
                ('locations', models.ManyToManyField(related_name='pieces', to='elvis.Location', blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('old_id', models.IntegerField(null=True, db_index=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('approved', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='piece',
            name='sources',
            field=models.ManyToManyField(related_name='pieces', to='elvis.Source', blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='tags',
            field=models.ManyToManyField(related_name='pieces', to='elvis.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='uploader',
            field=models.ForeignKey(related_name='pieces', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='piece',
            field=models.ForeignKey(related_name='movements', null=True, to='elvis.Piece', blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='sources',
            field=models.ManyToManyField(related_name='movements', to='elvis.Source', blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='tags',
            field=models.ManyToManyField(related_name='movements', to='elvis.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='uploader',
            field=models.ForeignKey(related_name='movements', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='collection_movements',
            field=models.ManyToManyField(related_name='user_downloads', to='elvis.Movement', blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='collection_pieces',
            field=models.ManyToManyField(related_name='user_downloads', to='elvis.Piece', blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='user',
            field=models.ForeignKey(related_name='downloads', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
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
