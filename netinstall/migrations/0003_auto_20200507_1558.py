# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netinstall', '0002_auto_20200507_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='configfile',
            name='content',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='configfile',
            name='filetype',
            field=models.ForeignKey(null=True, to='netinstall.ConfigFileType'),
        ),
    ]
