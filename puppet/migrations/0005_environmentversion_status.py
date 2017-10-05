# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0004_auto_20171005_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='environmentversion',
            name='status',
            field=models.CharField(choices=[('0', 'Undefined'), ('1', 'Deploying'), ('2', 'Deployed')], max_length=1, default='0'),
        ),
    ]
