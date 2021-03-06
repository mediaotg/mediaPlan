# Generated by Django 2.0.3 on 2018-04-12 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0005_auto_20180412_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='order',
            field=models.CharField(default=0, max_length=24),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='design',
            name='thumbnail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='setup.Image'),
        ),
    ]
