# Generated by Django 4.2.5 on 2023-11-21 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0033_familymembers_generalstatus_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientpathlab',
            name='LabTestSuggested',
        ),
    ]
