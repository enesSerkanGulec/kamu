# Generated by Django 2.2.7 on 2020-01-22 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200121_0914'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mesajlar',
            old_name='ilan',
            new_name='ilgili_ilan',
        ),
    ]
