# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netinstall', '0003_auto_20200507_1558'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boottemplate',
            old_name='installconifg',
            new_name='installconfig',
        ),
    ]
