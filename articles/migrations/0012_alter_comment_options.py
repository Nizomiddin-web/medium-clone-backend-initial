# Generated by Django 4.2.14 on 2024-10-06 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0011_alter_comment_options_alter_comment_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created_at'], 'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
    ]
