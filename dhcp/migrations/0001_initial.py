# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lease',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('IP', models.GenericIPAddressField()),
                ('MAC', models.CharField(max_length=18)),
            ],
            options={
                'ordering': ['IP', 'MAC'],
            },
        ),
        migrations.CreateModel(
            name='Subnet',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('active', models.BooleanField()),
                ('prefix', models.GenericIPAddressField()),
                ('mask', models.IntegerField()),
            ],
            options={
                'ordering': ['-active', 'name'],
            },
        ),
        migrations.AddField(
            model_name='lease',
            name='subnet',
            field=models.ForeignKey(to='dhcp.Subnet'),
        ),
    ]
