# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dhcp', '0003_lease_present'),
    ]

    operations = [
        migrations.AddField(
            model_name='lease',
            name='lease',
            field=models.BooleanField(default=False),
        ),
    ]
