# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import elvis.models.userprofile


class Migration(migrations.Migration):

    dependencies = [
        (b'elvis', b'0006_movement_taghierarchy'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name=b'UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id', unique=True)),
                (b'picture', models.ImageField(null=True, upload_to=elvis.models.userprofile.picture_path)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
