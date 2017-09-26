# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0003_auto_20170915_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('ipv4', models.GenericIPAddressField(protocol='IPv4', null=True)),
                ('ipv6', models.GenericIPAddressField(protocol='IPv6', null=True)),
                ('active', models.BooleanField(default=True)),
                ('domain', models.ForeignKey(to='nameserver.Domain')),
            ],
        ),
    ]
