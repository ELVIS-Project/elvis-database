# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elvis', '0002_auto_20150805_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='collection_collections',
            field=models.ManyToManyField(related_name='user_downloads', to='elvis.Collection', blank=True),
        ),
        migrations.AlterField(
            model_name='download',
            name='collection_composers',
            field=models.ManyToManyField(related_name='user_downloads', to='elvis.Composer', blank=True),
        ),
        migrations.AlterField(
            model_name='download',
            name='collection_movements',
            field=models.ManyToManyField(related_name='user_downloads', to='elvis.Movement', blank=True),
        ),
        migrations.AlterField(
            model_name='download',
            name='collection_pieces',
            field=models.ManyToManyField(related_name='user_downloads', to='elvis.Piece', blank=True),
        ),
    ]
