# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0014_auto_20171219_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='environment',
            field=models.ForeignKey(null=True, to='puppet.Environment',
                on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
