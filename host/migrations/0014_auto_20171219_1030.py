# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0005_auto_20170926_0912'),
        ('dhcp', '0005_subnet_domain'),
        ('host', '0013_auto_20171218_1626'),
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('domain', models.ForeignKey(to='nameserver.Domain')),
                ('v4subnet', models.ForeignKey(null=True, related_name='v4network', to='dhcp.Subnet')),
                ('v6subnet', models.ForeignKey(null=True, related_name='v6network', to='dhcp.Subnet')),
            ],
        ),
        migrations.AddField(
            model_name='interface',
            name='ipv6Type',
            field=models.IntegerField(choices=[(0, 'None'), (1, 'EUI-64'), (2, 'Static')], default=0),
        ),
        migrations.AddField(
            model_name='interface',
            name='network',
            field=models.ForeignKey(null=True, default=None, to='host.Network'),
        ),
    ]
