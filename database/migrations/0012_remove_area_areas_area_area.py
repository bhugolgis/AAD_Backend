# Generated by Django 4.2.5 on 2023-10-23 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0011_customuser_dispensary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='area',
            name='areas',
        ),
        migrations.AddField(
            model_name='area',
            name='area',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
