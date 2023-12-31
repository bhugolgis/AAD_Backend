# Generated by Django 4.2.5 on 2023-10-17 04:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='areaAmo_mo_name', to='database.area'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='health_Post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='healthpostAmo_mo_name', to='database.healthpost'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='ward',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wardAmo_mo_name', to='database.ward'),
        ),
        migrations.CreateModel(
            name='dispensary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dispensaryName', models.CharField(blank=True, max_length=255, null=True)),
                ('disphealthPost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disp_healthpost_name', to='database.healthpost')),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='dispensary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispensary_name', to='database.dispensary'),
        ),
    ]
