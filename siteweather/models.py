from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, User
from django.utils.safestring import mark_safe


class CityBlock(models.Model):
    city_name = models.CharField(verbose_name='Name of city', max_length=300)
    weather_main_description = models.CharField(verbose_name='Main description', max_length=300, blank=True)
    weather_full_description = models.CharField(verbose_name='Full description', max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp',)
    temperature = models.IntegerField(verbose_name='Temperature', default=0, blank=True)
    weather_icon = models.CharField(verbose_name='Icon', max_length=300, default='01d', blank=True)
    humidity = models.IntegerField(verbose_name='Humidity', default=0, blank=True)
    pressure = models.IntegerField(verbose_name='Pressure', default=0, blank=True)
    wind_speed = models.IntegerField(verbose_name='Wind speed', default=0, blank=True)
    country = models.CharField(verbose_name='Country', max_length=300, default='Unknown', blank=True)

    def get_absolute_url(self):
        return reverse('view_city', kwargs={'pk': self.pk})

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['-timestamp']
