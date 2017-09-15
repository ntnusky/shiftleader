# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dhcp', '0002_subnet_free'),
    ]

    operations = [
        migrations.AddField(
            model_name='lease',
            name='present',
            field=models.BooleanField(default=True),
        ),
    ]
