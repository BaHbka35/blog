# Generated by Django 3.2.8 on 2021-10-28 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_networks', '0005_auto_20211028_0825'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='likes',
        ),
    ]