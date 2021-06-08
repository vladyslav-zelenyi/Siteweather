# Generated by Django 3.1.1 on 2021-06-07 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('siteweather', '0002_customuser_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherDescription',
            fields=[
                ('short_description', models.CharField(blank=True, max_length=300, verbose_name='Main description')),
                ('full_description', models.CharField(blank=True, max_length=300, verbose_name='Full description')),
                ('weather_icon', models.CharField(blank=True, default='01d', max_length=300, primary_key=True, serialize=False, unique=True, verbose_name='Icon')),
            ],
        ),
        migrations.RemoveField(
            model_name='cityblock',
            name='weather_full_description',
        ),
        migrations.RemoveField(
            model_name='cityblock',
            name='weather_icon',
        ),
        migrations.RemoveField(
            model_name='cityblock',
            name='weather_main_description',
        ),
        migrations.AddField(
            model_name='cityblock',
            name='weather_description',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='siteweather.weatherdescription'),
        ),
    ]