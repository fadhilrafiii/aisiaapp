# Generated by Django 3.1.12 on 2022-08-24 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='xmax',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='xmin',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='ymax',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='ymin',
            field=models.FloatField(blank=True, null=True),
        ),
    ]