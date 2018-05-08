# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0003_auto_20150622_0915'),
        ('message', '0002_auto_20150713_0205'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='transaction',
            field=models.OneToOneField(related_name='thread', default=1, to='transaction.Transaction'),
            preserve_default=False,
        ),
    ]
