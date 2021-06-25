# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0011_partitionscheme'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='partition',
            field=models.ForeignKey(to='host.PartitionScheme', null=True,
            default=None, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
