# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0004_staticrecord'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staticrecord',
            options={'ordering': ['domain', 'name']},
        ),
    ]
