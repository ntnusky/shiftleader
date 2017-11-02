# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0009_auto_20171101_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportlog',
            name='file',
            field=models.CharField(null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='reportlog',
            name='line',
            field=models.IntegerField(null=True),
        ),
    ]
