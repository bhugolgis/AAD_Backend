# Generated by Django 4.2.6 on 2023-11-01 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0024_alter_healthcarecenters_healthcaretype'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalofficerconsultancy',
            name='referedToPrimaryConsultancy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='primaryconsultancy',
            name='referedToSecondaryConsultancy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tertiaryconsultancy',
            name='referedToTertiaryConsultancy',
            field=models.BooleanField(default=False),
        ),
    ]
