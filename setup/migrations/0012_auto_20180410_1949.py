# Generated by Django 2.0.3 on 2018-04-10 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0011_auto_20180410_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(max_length=1024, unique=True),
        ),
        migrations.AlterField(
            model_name='rate',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='setup.Client'),
        ),
    ]
