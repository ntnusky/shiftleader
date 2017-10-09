# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0006_auto_20171006_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='created',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='version',
            name='deployed',
            field=models.DateTimeField(null=True, auto_now=True),
        ),
    ]
