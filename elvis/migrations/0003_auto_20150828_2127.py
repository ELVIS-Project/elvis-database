# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('elvis', '0002_auto_20150828_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='composer',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='composer',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='genre',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='instrumentvoice',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='composer',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='composer',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='composer',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='instrumentvoice',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='instrumentvoice',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='instrumentvoice',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='language',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='language',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='language',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='location',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='movement',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='movement',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='piece',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='piece',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='piece',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
        migrations.AlterField(
            model_name='source',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='title',
            field=models.CharField(max_length=255, default='NOTITLE_ERROR'),
        ),
    ]
