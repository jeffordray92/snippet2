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
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', unique=True, max_length=100)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Subcategory',
                'verbose_name_plural': 'Subcategories',
            },
        ),
        migrations.RemoveField(
            model_name='category',
            name='parent_category',
        ),
        migrations.RemoveField(
            model_name='item',
            name='category',
        ),
        migrations.AddField(
            model_name='subcategory',
            name='parent_category',
            field=models.ForeignKey(to='item.Category'),
        ),
        migrations.AddField(
            model_name='item',
            name='subcategory',
            field=models.ForeignKey(default=1, to='item.Subcategory'),
            preserve_default=False,
        ),
    ]
