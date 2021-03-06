# Generated by Django 2.2.7 on 2020-01-20 21:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_sikayet_nedenleri'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sikayet_nedenleri',
            old_name='sikayet',
            new_name='neden',
        ),
        migrations.CreateModel(
            name='sikayet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateTimeField(auto_now_add=True)),
                ('hangi_ilan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.ilan')),
                ('kim', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('sikayet_nedeni', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.sikayet_nedenleri')),
            ],
        ),
    ]
