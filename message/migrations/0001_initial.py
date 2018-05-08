# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=500)),
                ('date_sent', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(related_name='message_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='message_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_sent'],
                'verbose_name': 'Message Entry',
                'verbose_name_plural': 'Message Entries',
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_initiated', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('receiver', models.ForeignKey(related_name='thread_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='thread_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_modified'],
                'verbose_name': 'Message Thread',
                'verbose_name_plural': 'Message Threads',
            },
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(to='message.Thread'),
        ),
    ]
