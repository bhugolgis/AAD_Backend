# Generated by Django 4.2.5 on 2024-01-15 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0059_merge_20240115_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='familymembers',
            name='randomBloodSugar',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='familymembers',
            name='relationship',
            field=models.CharField(blank=True, choices=[('Self', 'Self'), ('Mother', 'Mother'), ('Father', 'Father'), ('Spouse', 'Spouse'), ('Daughter', 'Daughter'), ('Grandson', 'Grandson'), ('Granddaughter', 'Granddaughter'), ('Grandmother', 'Grandmother'), ('Grandfather', 'Grandfather'), ('Uncle', 'Uncle'), ('Aunty', 'Aunty'), ('Nephew', 'Nephew'), ('Niece', 'Niece')], max_length=100, null=True),
        ),
    ]
