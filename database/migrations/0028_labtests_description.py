# Generated by Django 4.2.6 on 2023-11-06 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0027_labtests'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtests',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
