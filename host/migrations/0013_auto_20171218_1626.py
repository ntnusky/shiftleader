# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0012_host_partition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='host',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='host',
            name='domain',
        ),
        migrations.AlterField(
            model_name='host',
            name='status',
            field=models.CharField(max_length=1, choices=[(0, 'Operational'), (1, 'Provisioning'), (2, 'Installing'), (3, 'Puppet-Sign'), (4, 'Puppet-Ready'), (5, 'Puppet-Timeout'), (6, 'Puppet-Error')]),
        ),
    ]
