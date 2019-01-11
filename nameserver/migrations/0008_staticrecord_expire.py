# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0007_server_keyname'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticrecord',
            name='expire',
            field=models.DateField(null=True, default=None),
        ),
    ]
