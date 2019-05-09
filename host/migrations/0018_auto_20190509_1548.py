# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0017_auto_20181213_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='BootFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BootFileFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('order', models.IntegerField()),
                ('bootfile', models.ForeignKey(to='host.BootFile')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='BootFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('content', models.TextField()),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='host',
            name='partition',
        ),
        migrations.AddField(
            model_name='bootfilefragment',
            name='fragment',
            field=models.ForeignKey(to='host.BootFragment'),
        ),
        migrations.AddField(
            model_name='host',
            name='bootfile',
            field=models.ForeignKey(null=True, to='host.BootFile'),
        ),
    ]
