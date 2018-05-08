# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_auto_20150714_0445'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='distance_range',
            field=models.IntegerField(default=100),
        ),
    ]
