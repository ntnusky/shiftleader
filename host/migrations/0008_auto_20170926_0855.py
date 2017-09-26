# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0007_host_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='status',
            field=models.CharField(max_length=1, choices=[(0, 'Operational'), (1, 'Provisioning'), (2, 'Installing'), (3, 'Puppet-Sign'), (4, 'Puppet-run')]),
        ),
    ]
