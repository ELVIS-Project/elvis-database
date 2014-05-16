# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        (b'elvis', b'0007_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name', models.CharField(max_length=255)),
                (b'description', models.TextField(null=True, blank=True)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'updated', models.DateTimeField(auto_now=True)),
                (b'users', models.ManyToManyField(to=b'elvis.UserProfile', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
