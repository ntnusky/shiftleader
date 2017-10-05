# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0003_auto_20171005_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='environmentversion',
            name='deploynew',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='server',
            name='status',
            field=models.CharField(choices=[('0', 'Ok'), ('1', 'Checkin started'), ('2', 'r10k running'), ('3', 'r10k error'), ('4', 'Timeout')], max_length=1),
        ),
    ]
