# Generated by Django 2.0.3 on 2018-04-11 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='design',
            name='thumbnail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.Image'),
        ),
        migrations.DeleteModel(
            name='Thumbnail',
        ),
    ]
