# Generated by Django 5.1.3 on 2024-12-11 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messagerie', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='subject',
            field=models.CharField(default=2, max_length=255),
            preserve_default=False,
        ),
    ]