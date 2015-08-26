# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import elvis.models.attachment


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('attachment', models.FileField(max_length=512, null=True, upload_to=elvis.models.attachment.upload_path, blank=True)),
                ('source', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('uploader', models.ForeignKey(related_name='attachments', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('public', models.NullBooleanField()),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name_plural': 'collections',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('old_birth_date', models.DateField(null=True, blank=True)),
                ('old_death_date', models.DateField(null=True, blank=True)),
                ('birth_date', models.IntegerField(null=True, blank=True)),
                ('death_date', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('first_comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('first_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('attachments', models.ManyToManyField(related_name='downloads', to='elvis.Attachment', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalComposer',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('old_birth_date', models.DateField(null=True, blank=True)),
                ('old_death_date', models.DateField(null=True, blank=True)),
                ('birth_date', models.IntegerField(null=True, blank=True)),
                ('death_date', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('updated', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical composer',
            },
        ),
        migrations.CreateModel(
            name='InstrumentVoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Movement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('position', models.IntegerField(null=True, blank=True)),
                ('old_date_of_composition', models.DateField(null=True, blank=True)),
                ('old_date_of_composition2', models.DateField(null=True, blank=True)),
                ('date_of_composition', models.IntegerField(null=True, blank=True)),
                ('date_of_composition2', models.IntegerField(null=True, blank=True)),
                ('number_of_voices', models.IntegerField(null=True, blank=True)),
                ('religiosity', models.CharField(default=b'Unknown', max_length=50)),
                ('vocalization', models.CharField(default=b'Unknown', max_length=50)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attachments', models.ManyToManyField(related_name='movements', to='elvis.Attachment', blank=True)),
                ('collections', models.ManyToManyField(related_name='movements', to='elvis.Collection', blank=True)),
                ('composer', models.ForeignKey(related_name='movements', blank=True, to='elvis.Composer', null=True)),
                ('genres', models.ManyToManyField(related_name='movements', to='elvis.Genre', blank=True)),
                ('instruments_voices', models.ManyToManyField(related_name='movements', to='elvis.InstrumentVoice', blank=True)),
                ('languages', models.ManyToManyField(related_name='movements', to='elvis.Language', blank=True)),
                ('locations', models.ManyToManyField(related_name='movements', to='elvis.Location', blank=True)),
            ],
            options={
                'ordering': ['position', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('old_date_of_composition', models.DateField(null=True, blank=True)),
                ('old_date_of_composition2', models.DateField(null=True, blank=True)),
                ('date_of_composition', models.IntegerField(null=True, blank=True)),
                ('date_of_composition2', models.IntegerField(null=True, blank=True)),
                ('number_of_voices', models.IntegerField(null=True, blank=True)),
                ('religiosity', models.CharField(default=b'Unknown', max_length=50)),
                ('vocalization', models.CharField(default=b'Unknown', max_length=50)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attachments', models.ManyToManyField(related_name='pieces', to='elvis.Attachment', blank=True)),
                ('collections', models.ManyToManyField(related_name='pieces', to='elvis.Collection', blank=True)),
                ('composer', models.ForeignKey(related_name='pieces', blank=True, to='elvis.Composer', null=True)),
                ('genres', models.ManyToManyField(related_name='pieces', to='elvis.Genre', blank=True)),
                ('instruments_voices', models.ManyToManyField(related_name='pieces', to='elvis.InstrumentVoice', blank=True)),
                ('languages', models.ManyToManyField(related_name='pieces', to='elvis.Language', blank=True)),
                ('locations', models.ManyToManyField(related_name='pieces', to='elvis.Location', blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('approved', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='TagHierarchy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent', models.ForeignKey(related_name='has_hierarchy', blank=True, to='elvis.Tag', null=True)),
                ('tag', models.ForeignKey(related_name='in_hierarchy', to='elvis.Tag')),
            ],
            options={
                'verbose_name_plural': 'Tag Hierarchies',
            },
        ),
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('due_date', models.DateField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('project', models.ForeignKey(to='elvis.Project')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(to='elvis.UserProfile', blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='sources',
            field=models.ManyToManyField(related_name='pieces', to='elvis.Source', blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='tags',
            field=models.ManyToManyField(related_name='pieces', to='elvis.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='piece',
            name='uploader',
            field=models.ForeignKey(related_name='pieces', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='piece',
            field=models.ForeignKey(related_name='movements', blank=True, to='elvis.Piece', null=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='sources',
            field=models.ManyToManyField(related_name='movements', to='elvis.Source', blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='tags',
            field=models.ManyToManyField(related_name='movements', to='elvis.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='movement',
            name='uploader',
            field=models.ForeignKey(related_name='movements', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='download',
            name='collection_movements',
            field=models.ManyToManyField(to='elvis.Movement', blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='collection_pieces',
            field=models.ManyToManyField(to='elvis.Piece', blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='user',
            field=models.ForeignKey(related_name='downloads', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='discussion',
            name='project',
            field=models.ForeignKey(to='elvis.Project'),
        ),
        migrations.AddField(
            model_name='comment',
            name='discussion',
            field=models.ForeignKey(to='elvis.Discussion'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('elvis.location',),
        ),
    ]
