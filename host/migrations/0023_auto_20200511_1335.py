# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netinstall', '0006_auto_20200511_0958'),
        ('host', '0022_auto_20200507_1242'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PartitionScheme',
        ),
        migrations.AddField(
            model_name='host',
            name='template',
            field=models.ForeignKey(to='netinstall.BootTemplate', null=True),
        ),
    ]
