# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0005_auto_20170926_0912'),
        ('dhcp', '0004_lease_lease'),
    ]

    operations = [
        migrations.AddField(
            model_name='subnet',
            name='domain',
            field=models.ForeignKey(null=True, to='nameserver.Domain',
                                      on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
