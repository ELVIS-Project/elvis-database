# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        (b'elvis', b'0009_discussion'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name', models.CharField(max_length=255, null=True, blank=True)),
                (b'text', models.TextField()),
                (b'user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                (b'discussion', models.ForeignKey(to=b'elvis.Discussion', to_field='id')),
                (b'created', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
