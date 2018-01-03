# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0005_auto_20170926_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='algorithm',
            field=models.CharField(default='HMAC-MD5.SIG-ALG.REG.INT', max_length=28),
        ),
    ]
