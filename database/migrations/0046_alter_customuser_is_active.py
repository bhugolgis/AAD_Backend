# Generated by Django 4.2.5 on 2023-12-05 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0045_alter_familymembers_aadharcard_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
