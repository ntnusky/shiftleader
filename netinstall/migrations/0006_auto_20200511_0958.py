# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netinstall', '0005_auto_20200508_1551'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boottemplate',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='configfile',
            options={'ordering': ['filetype__name', 'name']},
        ),
        migrations.AlterModelOptions(
            name='configfiletype',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='operatingsystem',
            options={'ordering': ['name']},
        ),
    ]
