# Generated by Django 2.2.16 on 2022-02-11 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20220211_2110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-pub_date']},
        ),
    ]