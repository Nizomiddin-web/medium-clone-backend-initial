# Generated by Django 4.2.14 on 2024-10-17 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_remove_notification_read_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notification',
            name='read_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
