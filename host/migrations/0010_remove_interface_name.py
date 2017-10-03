# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0009_remove_interface_domain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='name',
        ),
    ]
