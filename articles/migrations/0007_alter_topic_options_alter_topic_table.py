# Generated by Django 4.2.14 on 2024-09-30 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_alter_article_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'Topic', 'verbose_name_plural': 'Topics'},
        ),
        migrations.AlterModelTable(
            name='topic',
            table='topic',
        ),
    ]
