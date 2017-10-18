# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0011_partitionscheme'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='partition',
            field=models.ForeignKey(to='host.PartitionScheme', null=True, default=None),
        ),
    ]
