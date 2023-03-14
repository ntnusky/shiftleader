# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0016_remove_interface_ipv6type'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('shortname', models.CharField(max_length=20)),
                ('kernelname', models.CharField(max_length=64)),
                ('kernelurl', models.CharField(max_length=256)),
                ('kernelsum', models.CharField(null=True, default=None, max_length=130)),
                ('initrdname', models.CharField(max_length=64)),
                ('initrdurl', models.CharField(max_length=256)),
                ('initrdsum', models.CharField(null=True, default=None, max_length=130)),
            ],
        ),
        migrations.AddField(
            model_name='host',
            name='os',
            field=models.ForeignKey(null=True, to='host.OperatingSystem',
            on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
