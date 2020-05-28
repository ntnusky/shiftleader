# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0021_host_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bootfile',
            name='filetype',
            field=models.IntegerField(choices=[(0, 'Unset'), (1, 'Bootfile'), (2, 'Postinstall script')], default=0),
        ),
    ]
