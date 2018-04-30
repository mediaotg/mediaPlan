# Generated by Django 2.0.3 on 2018-03-27 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0007_auto_20180327_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='recurrence',
            field=models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('full campaign', 'Full Campaign')], default='weekly', max_length=15),
        ),
        migrations.DeleteModel(
            name='Recurrence',
        ),
    ]
