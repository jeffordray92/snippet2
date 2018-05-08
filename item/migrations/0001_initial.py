# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import swapp_api.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('parent_category', models.ForeignKey(blank=True, to='item.Category', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('photo', swapp_api.fields.AutoResizeImageField(max_length=500, null=True, upload_to=b'item/', blank=True)),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('price_range_minimum', models.PositiveIntegerField()),
                ('price_range_maximum', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=1000)),
                ('is_available', models.BooleanField(default=True)),
                ('category', models.ForeignKey(to='item.Category')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_posted'],
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag_name', models.CharField(unique=True, max_length=100)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
            ],
            options={
                'ordering': ['tag_name'],
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(to='item.Tag', null=True, blank=True),
        ),
    ]
