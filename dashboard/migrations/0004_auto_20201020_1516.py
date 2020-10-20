# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20201020_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='system',
            field=models.IntegerField(choices=[(0, 'Undefined'), (1, 'DNS'), (2, 'Puppet')]),
        ),
    ]
