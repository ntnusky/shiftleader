# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0010_remove_interface_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartitionScheme',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('content', models.TextField()),
            ],
        ),
    ]
