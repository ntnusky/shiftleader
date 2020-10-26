# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0013_auto_20201020_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='status',
            field=models.CharField(max_length=1, choices=[('0', 'Ok'), ('1', 'Scheduled'), ('2', 'Deploying'), ('3', 'r10k-failed'), ('4', 'Timeout')]),
        ),
    ]
