# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('elvis', '0003_auto_20150828_2127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='description',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='old_id',
        ),
        migrations.AddField(
            model_name='attachment',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='updated',
            field=models.DateTimeField(null=True, auto_now=True),
        ),
    ]
