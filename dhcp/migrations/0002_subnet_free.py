# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dhcp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subnet',
            name='free',
            field=models.IntegerField(default=-1),
        ),
    ]
