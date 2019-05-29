# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0018_auto_20190509_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='postinstallscript',
            field=models.ForeignKey(to='host.BootFile', related_name='scripthosts', null=True),
        ),
    ]
