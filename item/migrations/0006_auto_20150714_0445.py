# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0005_swaphistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='latitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
        migrations.AddField(
            model_name='item',
            name='longitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
    ]
