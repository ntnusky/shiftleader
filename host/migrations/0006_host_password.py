# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0005_auto_20170915_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='password',
            field=models.CharField(null=True, max_length=64),
        ),
    ]
