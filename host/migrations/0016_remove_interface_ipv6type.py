# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0015_auto_20180119_1048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='ipv6Type',
        ),
    ]
