# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0006_auto_20150714_0445'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='condition',
            field=models.BooleanField(default=True),
        ),
    ]
