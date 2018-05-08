# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notification', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(default=b'offer', max_length=10, choices=[(b'offer', b'Offer'), (b'accept', b'Accept'), (b'reject', b'Reject')])),
                ('action_from', models.ForeignKey(related_name='notifications_sent', to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(related_name='notifications_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_created'],
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
            },
        ),
    ]
