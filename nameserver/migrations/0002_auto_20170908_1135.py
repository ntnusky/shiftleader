# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='key',
            field=models.CharField(null=True, max_length=200),
        ),
    ]
