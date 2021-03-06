# Generated by Django 3.1.7 on 2021-06-15 12:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventmaker', '0003_event_request_participants'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event_request',
            name='participants',
        ),
        migrations.AddField(
            model_name='event_request',
            name='participants',
            field=models.ManyToManyField(related_name='participants', to=settings.AUTH_USER_MODEL),
        ),
    ]
