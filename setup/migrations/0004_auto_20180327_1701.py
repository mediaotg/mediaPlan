# Generated by Django 2.0.3 on 2018-03-27 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0003_auto_20180323_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='uplaods/%Y/%m/')),
            ],
        ),
        migrations.AlterField(
            model_name='targetgroup',
            name='name',
            field=models.CharField(max_length=1024, unique=True),
        ),
    ]
