# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netinstall', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boottemplate',
            name='installconifg',
            field=models.ForeignKey(to='netinstall.ConfigFile', related_name='bt_inst', null=True),
        ),
        migrations.AlterField(
            model_name='boottemplate',
            name='os',
            field=models.ForeignKey(null=True, to='netinstall.OperatingSystem'),
        ),
        migrations.AlterField(
            model_name='boottemplate',
            name='postinstall',
            field=models.ForeignKey(to='netinstall.ConfigFile', related_name='bt_postinst', null=True),
        ),
        migrations.AlterField(
            model_name='boottemplate',
            name='tftpconfig',
            field=models.ForeignKey(to='netinstall.ConfigFile', related_name='bt_tftp', null=True),
        ),
    ]
