# Generated by Django 4.2.14 on 2024-10-10 06:10

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0016_usertopicfollow'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserTopicFollow',
            new_name='TopicFollow',
        ),
    ]