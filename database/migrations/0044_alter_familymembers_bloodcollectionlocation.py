# Generated by Django 4.2.5 on 2023-12-01 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0043_familymembers_vulnerable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familymembers',
            name='bloodCollectionLocation',
            field=models.CharField(blank=True, choices=[('Home', 'Home'), ('Center', 'Center'), ('Denied', 'Denied'), ('Not Required', 'Not Required')], max_length=20, null=True),
        ),
    ]
