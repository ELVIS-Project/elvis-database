# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        (b'elvis', b'0003_corpus'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'user', models.ForeignKey(to_field='id', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'attachments', models.ManyToManyField(to=b'elvis.Attachment', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
