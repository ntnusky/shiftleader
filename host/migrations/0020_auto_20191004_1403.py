# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0019_host_postinstallscript'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='bootfile',
            name='filetype',
            field=models.IntegerField(default=0, choices=[(0, 'unset'), (1, 'Bootfile'), (2, 'Postinstall script')]),
        ),
    ]
