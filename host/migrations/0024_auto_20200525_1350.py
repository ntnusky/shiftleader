# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0023_auto_20200511_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='template',
            field=models.ForeignKey(to='netinstall.BootTemplate', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
