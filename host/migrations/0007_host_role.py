# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0002_auto_20170901_1212'),
        ('host', '0006_host_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='role',
            field=models.ForeignKey(to='puppet.Role', null=True,
                on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
