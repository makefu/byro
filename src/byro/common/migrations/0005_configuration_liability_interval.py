# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-13 14:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20180111_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='liability_interval',
            field=models.IntegerField(default=36, help_text='For which interval should remaining fees be calculated?', verbose_name='Liability interval'),
        ),
    ]
