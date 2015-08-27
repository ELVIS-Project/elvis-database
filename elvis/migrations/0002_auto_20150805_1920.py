# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='collection_collections',
            field=models.ManyToManyField(to='elvis.Collection', blank=True),
        ),
        migrations.AddField(
            model_name='download',
            name='collection_composers',
            field=models.ManyToManyField(to='elvis.Composer', blank=True),
        ),
    ]
