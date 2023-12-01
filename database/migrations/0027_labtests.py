# Generated by Django 4.2.6 on 2023-11-06 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0026_merge_20231103_1751'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabTests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testName', models.CharField(blank=True, max_length=500, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('isActive', models.BooleanField(default=True)),
            ],
        ),
    ]