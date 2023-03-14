# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0011_auto_20201028_1224'),
        ('host', '0024_auto_20200525_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='dns',
            field=models.ForeignKey(null=True, default=None,
            to='nameserver.Forward', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
