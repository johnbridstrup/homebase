# Generated by Django 4.2.13 on 2024-06-19 21:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('sensor_type', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('AC', 'Active'), ('IN', 'Inactive'), ('UR', 'Unregistered')], default='UR', max_length=2)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sensors', to='rooms.room')),
            ],
        ),
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='sensors.sensor')),
            ],
        ),
    ]