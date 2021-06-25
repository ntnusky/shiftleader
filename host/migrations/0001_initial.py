# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0002_auto_20170901_1212'),
        ('nameserver', '0002_auto_20170908_1135'),
        ('dhcp', '0002_subnet_free'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('status', models.CharField(max_length=1, choices=[(0, 'Operational'), (1, 'Provisioning'), (2, 'Installing')])),
                ('environment', models.ForeignKey(to='puppet.Environment',
                                                    on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('ifname', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=64)),
                ('mac', models.CharField(max_length=64)),
                ('ipv4', models.GenericIPAddressField(protocol='IPv4', null=True)),
                ('ipv6', models.GenericIPAddressField(protocol='IPv6', null=True)),
                ('domain', models.ForeignKey(to='nameserver.Domain',
                                      on_delete=django.db.models.deletion.SET_NULL)),
                ('host', models.ForeignKey(to='host.Host',
                                            on_delete=django.db.models.deletion.PROTECT)),
                ('ipv4Lease', models.ForeignKey(to='dhcp.Lease', null=True,
                                            on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
    ]
