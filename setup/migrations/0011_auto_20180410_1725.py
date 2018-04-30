# Generated by Django 2.0.3 on 2018-04-10 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0010_auto_20180328_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='logo',
            field=models.ForeignKey(default=77, on_delete=django.db.models.deletion.CASCADE, to='setup.Image'),
        ),
        migrations.AlterField(
            model_name='client',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setup.Client'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='contactName',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='logo',
            field=models.ForeignKey(default=77, on_delete=django.db.models.deletion.CASCADE, to='setup.Image'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='phone',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='targetGroups',
            field=models.ManyToManyField(blank=True, null=True, related_name='publications', to='setup.TargetGroup'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='publication',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='setup.Publication'),
        ),
    ]
