# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (b'elvis', b'0010_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Todo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name', models.CharField(max_length=255, null=True, blank=True)),
                (b'description', models.TextField(null=True, blank=True)),
                (b'project', models.ForeignKey(to=b'elvis.Project', to_field='id')),
                (b'assigned_to', models.ForeignKey(to_field='id', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                (b'due_date', models.DateField(null=True, blank=True)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
