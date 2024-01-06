# Generated by Django 4.2.5 on 2024-01-05 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0054_customuser_created_date_customuser_usersections'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientsPathlabrecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='area',
            name='areas',
            field=models.TextField(blank=True, max_length=1000, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='medicalofficerconsultancy',
            name='MoPatientsPathReport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moPatientsPathReport', to='database.patientspathlabrecords'),
        ),
        migrations.AlterField(
            model_name='patientpathlabreports',
            name='patientPathLab',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patientPathLabReports', to='database.patientspathlabrecords'),
        ),
        migrations.AlterField(
            model_name='primaryconsultancy',
            name='PriPatientsPathReport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PriPatientsPathReport', to='database.patientspathlabrecords'),
        ),
        migrations.AlterField(
            model_name='secondaryconsultancy',
            name='SecPatientsPathReport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='SecPatientsPathReport', to='database.patientspathlabrecords'),
        ),
        migrations.AlterField(
            model_name='tertiaryconsultancy',
            name='TerPatientsPathReport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TerPatientsPathReport', to='database.patientspathlabrecords'),
        ),
    ]
