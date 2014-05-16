# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (b'elvis', b'0005_piece'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Movement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                (b'title', models.CharField(max_length=255)),
                (b'uploader', models.ForeignKey(to_field='id', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                (b'piece', models.ForeignKey(to_field='id', blank=True, to=b'elvis.Piece', null=True)),
                (b'corpus', models.ForeignKey(to_field='id', blank=True, to=b'elvis.Corpus', null=True)),
                (b'composer', models.ForeignKey(to_field='id', blank=True, to=b'elvis.Composer', null=True)),
                (b'date_of_composition', models.DateField(null=True, blank=True)),
                (b'number_of_voices', models.IntegerField(null=True, blank=True)),
                (b'comment', models.TextField(null=True, blank=True)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'updated', models.DateTimeField(auto_now=True)),
                (b'tags', models.ManyToManyField(to=b'elvis.Tag', null=True, blank=True)),
                (b'attachments', models.ManyToManyField(to=b'elvis.Attachment', null=True, blank=True)),
            ],
            options={
                'ordering': [b'title'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'TagHierarchy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'tag', models.ForeignKey(to=b'elvis.Tag', to_field='id')),
                (b'parent', models.ForeignKey(to_field='id', blank=True, to=b'elvis.Tag', null=True)),
            ],
            options={
                'verbose_name_plural': b'Tag Hierarchies',
            },
            bases=(models.Model,),
        ),
    ]
