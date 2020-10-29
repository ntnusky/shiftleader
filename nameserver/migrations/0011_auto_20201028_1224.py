# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nameserver', '0010_auto_20201028_1031'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cname',
            unique_together=set([('name', 'domain')]),
        ),
        migrations.AlterUniqueTogether(
            name='forward',
            unique_together=set([('name', 'domain')]),
        ),
        migrations.AlterUniqueTogether(
            name='reverse',
            unique_together=set([('name', 'domain')]),
        ),
    ]
