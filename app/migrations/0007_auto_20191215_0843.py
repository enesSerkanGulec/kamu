# Generated by Django 2.2.7 on 2019-12-15 05:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_ilan_yayinda'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resim',
            options={'ordering': ['ilan']},
        ),
        migrations.RemoveField(
            model_name='mesajlar',
            name='sahip',
        ),
    ]
