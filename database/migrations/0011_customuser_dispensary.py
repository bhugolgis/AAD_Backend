# Generated by Django 4.2.5 on 2023-10-22 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0010_customuser_health_post_customuser_ward_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='dispensary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispensary_name', to='database.dispensary'),
        ),
    ]
