# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0003_auto_20170912_1352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='ipv4',
        ),
    ]
