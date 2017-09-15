# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0002_auto_20170912_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='ipv4Lease',
            field=models.OneToOneField(null=True, to='dhcp.Lease'),
        ),
    ]
