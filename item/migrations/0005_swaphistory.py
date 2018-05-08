# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transaction', '0002_notification'),
        ('item', '0004_auto_20150611_0539'),
    ]

    operations = [
        migrations.CreateModel(
            name='SwapHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('item1', models.ForeignKey(related_name='swap_history_first_item', to='item.Item')),
                ('item2', models.ForeignKey(related_name='swap_history_second_item', to='item.Item')),
                ('transaction_trail', models.ForeignKey(to='transaction.Transaction')),
                ('user1', models.ForeignKey(related_name='swap_history_first_user', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(related_name='swap_history_second_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
                'verbose_name': 'Swap History',
                'verbose_name_plural': 'Swap History',
            },
        ),
    ]
