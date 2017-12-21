# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dhcp', '0005_subnet_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='subnet',
            name='ipversion',
            field=models.IntegerField(default=4),
        ),
    ]
