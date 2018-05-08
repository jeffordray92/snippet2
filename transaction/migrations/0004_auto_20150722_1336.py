# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0003_auto_20150622_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='transaction',
            field=models.ForeignKey(related_name='notification', blank=True, to='transaction.Transaction', null=True),
        ),
    ]
