# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_approved', models.NullBooleanField()),
                ('date_approved', models.DateTimeField(null=True, blank=True)),
                ('is_read', models.BooleanField(default=False)),
                ('item1', models.ForeignKey(related_name='item1', to='item.Item')),
                ('item2', models.ForeignKey(related_name='item2', to='item.Item')),
            ],
            options={
                'ordering': ['date_created'],
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]
