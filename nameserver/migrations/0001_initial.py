# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('address', models.GenericIPAddressField()),
                ('key', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='domain',
            name='server',
            field=models.ForeignKey(to='nameserver.Server',
                on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
