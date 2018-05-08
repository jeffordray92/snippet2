# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_auto_20150611_0255'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='current_latitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_longitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
    ]
