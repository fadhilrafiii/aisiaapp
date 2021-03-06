# Generated by Django 3.2.14 on 2022-07-27 08:28

from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Object',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('img_url', models.CharField(max_length=200, verbose_name='url')),
                ('img_name', models.CharField(max_length=50, verbose_name='name')),
                ('img_size', models.IntegerField()),
                ('img_dimension', djongo.models.fields.JSONField()),
            ],
            options={
                'db_table': 'objects',
            },
        ),
    ]
