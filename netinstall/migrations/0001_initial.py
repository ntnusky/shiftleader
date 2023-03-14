# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BootTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ConfigFile',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ConfigFileType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('shortname', models.CharField(max_length=20)),
                ('kernelname', models.CharField(max_length=64)),
                ('kernelurl', models.CharField(max_length=256)),
                ('kernelsum', models.CharField(max_length=130, default=None, null=True)),
                ('initrdname', models.CharField(max_length=64)),
                ('initrdurl', models.CharField(max_length=256)),
                ('initrdsum', models.CharField(max_length=130, default=None, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='configfile',
            name='filetype',
            field=models.ForeignKey(to='netinstall.ConfigFileType',
                on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='boottemplate',
            name='installconifg',
            field=models.ForeignKey(to='netinstall.ConfigFile',
                related_name='bt_inst', 
                on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='boottemplate',
            name='os',
            field=models.ForeignKey(to='netinstall.OperatingSystem',
                on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='boottemplate',
            name='postinstall',
            field=models.ForeignKey(to='netinstall.ConfigFile', 
                related_name='bt_postinst',
                on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='boottemplate',
            name='tftpconfig',
            field=models.ForeignKey(to='netinstall.ConfigFile', 
                related_name='bt_tftp',
                on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
