# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0002_auto_20170901_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvironmentVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('signature', models.CharField(max_length=64)),
                ('started', models.CharField(max_length=64)),
                ('finished', models.CharField(max_length=64)),
                ('success', models.BooleanField()),
                ('environment', models.ForeignKey(to='puppet.Environment',
                    on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('last_checkin', models.DateTimeField()),
                ('status', models.CharField(max_length=1, choices=[('0', 'Ok'), ('1', 'r10k running'), ('2', 'r10k error')])),
                ('todeploy', models.ManyToManyField(to='puppet.Environment')),
            ],
        ),
        migrations.AddField(
            model_name='environmentversion',
            name='server',
            field=models.ForeignKey(to='puppet.Server',
            on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
