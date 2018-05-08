# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0002_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='is_read',
        ),
        migrations.AddField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notification',
            name='transaction',
            field=models.OneToOneField(related_name='notification', null=True, blank=True, to='transaction.Transaction'),
        ),
    ]
