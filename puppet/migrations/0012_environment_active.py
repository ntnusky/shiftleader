# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0011_auto_20171101_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='environment',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
