# Generated by Django 4.2.14 on 2024-10-06 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0012_alter_comment_options'),
        ('users', '0008_alter_recommendation_less_recommend_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendation',
            name='less_recommend',
            field=models.ManyToManyField(blank=True, null=True, related_name='less_recommend', to='articles.article'),
        ),
        migrations.AlterField(
            model_name='recommendation',
            name='more_recommend',
            field=models.ManyToManyField(blank=True, null=True, related_name='more_recommend', to='articles.article'),
        ),
    ]
