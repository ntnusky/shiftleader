# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0008_staticrecord_expire'),
    ]

    operations = [
        migrations.CreateModel(
            name='CName',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('record_type', models.IntegerField(choices=[(0, 'Manual'), (1, 'Automatic'), (2, 'Host')])),
                ('target', models.CharField(max_length=200)),
                ('domain', models.ForeignKey(to='nameserver.Domain',
                    on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Forward',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('record_type', models.IntegerField(choices=[(0, 'Manual'), (1, 'Automatic'), (2, 'Host')])),
                ('ipv4', models.GenericIPAddressField(protocol='IPv4', null=True)),
                ('ipv6', models.GenericIPAddressField(protocol='IPv6', null=True)),
                ('reverse', models.BooleanField()),
                ('domain', models.ForeignKey(to='nameserver.Domain',
                    on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reverse',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('record_type', models.IntegerField(choices=[(0, 'Manual'), (1, 'Automatic'), (2, 'Host')])),
                ('target', models.CharField(max_length=200)),
                ('domain', models.ForeignKey(to='nameserver.Domain',
                    on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
    ]
