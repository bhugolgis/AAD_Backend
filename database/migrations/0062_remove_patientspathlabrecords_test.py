# Generated by Django 4.2.5 on 2024-01-15 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0061_patientspathlabrecords_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientspathlabrecords',
            name='test',
        ),
    ]