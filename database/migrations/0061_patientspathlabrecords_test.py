# Generated by Django 4.2.5 on 2024-01-15 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0060_familymembers_randombloodsugar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientspathlabrecords',
            name='test',
            field=models.BooleanField(default=True),
        ),
    ]
