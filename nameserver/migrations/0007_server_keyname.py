# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0006_server_algorithm'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='keyname',
            field=models.CharField(max_length=200, default='update'),
        ),
    ]
