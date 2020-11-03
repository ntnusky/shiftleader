# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('system', models.IntegerField(choices=[(0, 'Undefined'), (1, 'DNS'), (1, 'Puppet')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.IntegerField(choices=[(0, 'Ready'), (1, 'In-Progress'), (2, 'Finished')])),
                ('typeid', models.IntegerField()),
                ('payload', models.TextField()),
            ],
        ),
    ]
