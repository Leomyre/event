# Generated by Django 5.1.3 on 2024-12-11 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.CharField(default=2, max_length=200),
            preserve_default=False,
        ),
    ]