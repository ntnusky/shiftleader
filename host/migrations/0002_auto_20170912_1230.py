# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0002_auto_20170908_1135'),
        ('host', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='domain',
            field=models.ForeignKey(default=None, to='nameserver.Domain'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='interface',
            name='primary',
            field=models.BooleanField(default=False),
        ),
    ]
