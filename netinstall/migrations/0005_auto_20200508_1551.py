# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netinstall', '0004_auto_20200507_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boottemplate',
            name='installconfig',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='netinstall.ConfigFile', related_name='bt_inst', null=True),
        ),
        migrations.AlterField(
            model_name='boottemplate',
            name='os',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='netinstall.OperatingSystem', null=True),
        ),
        migrations.AlterField(
            model_name='boottemplate',
            name='postinstall',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='netinstall.ConfigFile', related_name='bt_postinst', null=True),
        ),
        migrations.AlterField(
            model_name='boottemplate',
            name='tftpconfig',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='netinstall.ConfigFile', related_name='bt_tftp', null=True),
        ),
        migrations.AlterField(
            model_name='configfile',
            name='filetype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='netinstall.ConfigFileType', null=True),
        ),
    ]
