# Generated by Django 4.2.14 on 2024-09-29 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('description', models.CharField()),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
    ]
