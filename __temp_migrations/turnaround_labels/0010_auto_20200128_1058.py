# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-01-28 15:58
from __future__ import unicode_literals

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('turnaround_labels', '0009_auto_20200122_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='manip_1',
            field=otree.db.models.StringField(max_length=10000, null=True, verbose_name=''),
        ),
        migrations.AddField(
            model_name='player',
            name='manip_2',
            field=otree.db.models.StringField(max_length=10000, null=True, verbose_name=''),
        ),
        migrations.AddField(
            model_name='player',
            name='manip_3',
            field=otree.db.models.StringField(max_length=10000, null=True, verbose_name=''),
        ),
        migrations.AddField(
            model_name='player',
            name='manip_4',
            field=otree.db.models.StringField(max_length=10000, null=True, verbose_name=''),
        ),
        migrations.AddField(
            model_name='player',
            name='manip_5',
            field=otree.db.models.StringField(max_length=10000, null=True, verbose_name=''),
        ),
    ]
