# Generated by Django 3.2.8 on 2021-10-28 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_networks', '0004_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='entry_id',
            new_name='entry',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='user_id',
            new_name='user',
        ),
    ]
