# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0005_environmentversion_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('signature', models.CharField(max_length=64)),
                ('status', models.CharField(choices=[('0', 'Scheduled'), ('1', 'Deploying'), ('2', 'Deployed'), ('3', 'Error')], default='0', max_length=1)),
                ('created', models.DateTimeField(null=True)),
                ('deployed', models.DateTimeField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='environmentversion',
            name='environment',
        ),
        migrations.RemoveField(
            model_name='environmentversion',
            name='server',
        ),
        migrations.AlterModelOptions(
            name='environment',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='environment',
            name='active',
        ),
        migrations.RemoveField(
            model_name='role',
            name='active',
        ),
        migrations.RemoveField(
            model_name='server',
            name='todeploy',
        ),
        migrations.AddField(
            model_name='environment',
            name='last_deployed',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='last_deployed',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='last_checkin',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='status',
            field=models.CharField(choices=[('0', 'Ok'), ('1', 'Checkin started'), ('2', 'r10k is running'), ('3', 'r10k failed'), ('4', 'Timeout')], max_length=1),
        ),
        migrations.DeleteModel(
            name='EnvironmentVersion',
        ),
        migrations.AddField(
            model_name='version',
            name='environment',
            field=models.ForeignKey(to='puppet.Environment',
            on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='version',
            name='server',
            field=models.ForeignKey(to='puppet.Server',
            on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
