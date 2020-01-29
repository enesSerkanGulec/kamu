# Generated by Django 2.2.7 on 2020-01-29 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20200129_0059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mesajlar',
            name='gonderen',
        ),
        migrations.RemoveField(
            model_name='mesajlar',
            name='ilgili_ilan',
        ),
        migrations.AddField(
            model_name='mesaj',
            name='gonderen_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='mesaj',
            name='gonderilen_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='mesaj',
            name='okundu',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mesaj',
            name='silindi',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='mesaj',
            name='ilgili_ilan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ilan'),
        ),
        migrations.AlterField(
            model_name='mesaj',
            name='mesaj_metni',
            field=models.TextField(null=True),
        ),
        migrations.DeleteModel(
            name='MesajHareketleri',
        ),
        migrations.DeleteModel(
            name='Mesajlar',
        ),
    ]
