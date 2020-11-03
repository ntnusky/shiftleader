# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0009_cname_forward_reverse'),
    ]

    operations = [
        migrations.AddField(
            model_name='cname',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='alias',
            field=models.CharField(max_length=200, null=True, default=None),
        ),
        migrations.AddField(
            model_name='forward',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='reverse',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
