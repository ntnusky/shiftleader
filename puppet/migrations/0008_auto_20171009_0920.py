# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0007_auto_20171006_1352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='server',
            options={'ordering': ['name']},
        ),
    ]
