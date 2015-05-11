# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
import elvis.models.composer
import elvis.models.userprofile
import elvis.models.attachment


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0012_auto_20140515_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='attachment',
            field=models.FileField(max_length=512, null=True, upload_to=elvis.models.attachment.upload_path, blank=True),
        ),
        migrations.AlterField(
            model_name='composer',
            name='picture',
            field=models.ImageField(null=True, upload_to=elvis.models.composer.picture_path, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(null=True, upload_to=elvis.models.userprofile.picture_path, blank=True),
        ),
    ]
