# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0020_auto_20191004_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='group',
            field=models.ForeignKey(to='host.HostGroup', null=True,
                on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
