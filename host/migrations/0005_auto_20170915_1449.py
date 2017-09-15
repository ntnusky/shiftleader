# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0004_remove_interface_ipv4'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='host',
            options={'ordering': ['domain', 'name']},
        ),
    ]
