# Generated by Django 2.2.16 on 2022-02-20 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_follow'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='user_author'),
        ),
    ]