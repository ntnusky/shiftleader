# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0012_host_partition'),
        ('puppet', '0008_auto_20171009_0920'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('noop', models.BooleanField()),
                ('noop_pending', models.BooleanField()),
                ('configuration_version', models.CharField(max_length=32)),
                ('puppet_version', models.CharField(max_length=12)),
                ('status', models.IntegerField(choices=[(0, 'Unchanged'), (1, 'Changed'), (2, 'Failed')])),
                ('time', models.DateTimeField()),
                ('environment', models.ForeignKey(to='puppet.Environment')),
                ('host', models.ForeignKey(to='host.Host')),
            ],
        ),
        migrations.CreateModel(
            name='ReportLog',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('level', models.IntegerField(choices=[(0, 'Critical'), (1, 'Emergency'), (2, 'Alert'), (3, 'Error'), (4, 'Warning'), (5, 'Notice'), (6, 'Info'), (7, 'Debug')])),
                ('message', models.TextField()),
                ('source', models.TextField()),
                ('line', models.IntegerField()),
                ('file', models.CharField(max_length=128)),
                ('time', models.DateTimeField()),
                ('report', models.ForeignKey(to='puppet.Report')),
            ],
        ),
        migrations.CreateModel(
            name='ReportMetric',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('metricType', models.IntegerField(choices=[(0, 'Time'), (1, 'Resource'), (2, 'Event'), (3, 'Change')])),
                ('name', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=64)),
                ('report', models.ForeignKey(to='puppet.Report')),
            ],
        ),
        migrations.CreateModel(
            name='ReportTag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='reportlog',
            name='tags',
            field=models.ManyToManyField(related_name='entries', to='puppet.ReportTag'),
        ),
    ]
