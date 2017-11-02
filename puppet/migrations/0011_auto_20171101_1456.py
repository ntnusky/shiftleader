# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0010_auto_20171101_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportlog',
            name='level',
            field=models.IntegerField(choices=[(0, 'Crit'), (1, 'Emerg'), (2, 'Alert'), (3, 'Err'), (4, 'Warning'), (5, 'Notice'), (6, 'Info'), (7, 'Debug')]),
        ),
        migrations.AlterField(
            model_name='reporttag',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
