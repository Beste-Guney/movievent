# Generated by Django 3.1.7 on 2021-06-16 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_friend_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favourite_style',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
