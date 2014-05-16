# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import elvis.models.attachment


class Migration(migrations.Migration):

    dependencies = [
        (b'elvis', b'0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                (b'attachment', models.FileField(max_length=512, null=True, upload_to=elvis.models.attachment.upload_path)),
                (b'uploader', models.ForeignKey(to_field='id', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                (b'description', models.CharField(max_length=255, null=True, blank=True)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
