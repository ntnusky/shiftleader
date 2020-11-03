# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0012_environment_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='environment',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('name', 'environment')]),
        ),
    ]
