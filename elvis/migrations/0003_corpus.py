# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (b'elvis', b'0002_attachment'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'Corpus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                (b'creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                (b'title', models.CharField(max_length=255, null=True, blank=True)),
                (b'comment', models.TextField(null=True, blank=True)),
                (b'created', models.DateTimeField(auto_now_add=True)),
                (b'updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': [b'title'],
                'verbose_name_plural': b'corpora',
            },
            bases=(models.Model,),
        ),
    ]
