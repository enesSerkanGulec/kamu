# Generated by Django 2.2.7 on 2020-01-16 06:41

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200115_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='kurum_mahalle',
        ),
        migrations.AddField(
            model_name='user',
            name='kurum_mahalle',
            field=smart_selects.db_fields.ChainedForeignKey(chained_field='kurum_ilce', chained_model_field='ilcee', null=True, on_delete=django.db.models.deletion.CASCADE, to='app.mahalle'),
        ),
    ]
