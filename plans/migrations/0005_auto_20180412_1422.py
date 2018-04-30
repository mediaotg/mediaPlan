# Generated by Django 2.0.3 on 2018-04-12 14:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0004_auto_20180411_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediaplan',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mediaplan',
            name='shuffle',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='mediaplan',
            name='starter',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='mediaplan',
            name='status',
            field=models.CharField(choices=[('draft', 'draft'), ('approve', 'awaiting approval'), ('book', 'book publications'), ('design', 'awaiting design'), ('send', 'sending to publications'), ('complete', 'published'), ('cancelled', 'cancelled')], default='draft', max_length=15),
        ),
    ]
