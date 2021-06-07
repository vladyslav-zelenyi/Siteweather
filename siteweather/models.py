from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.postgres.fields import ArrayField

ROLE_CHOICES = (
    ('Standard', 'Standard'),
    ('Premium', 'Premium'),
)


class CustomUser(AbstractUser):
    photo = models.ImageField(null=True, blank=True, upload_to='users/%Y/%m/%d')
    phone_number = models.CharField(verbose_name='Phone number', max_length=15, blank=True)
    user_city = models.CharField(verbose_name='City', max_length=50, blank=True)
    date_of_birth = models.DateField(verbose_name='Date of birth', null=True, blank=False)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='Standard', verbose_name='Role')

    def colored_premium(self):
        if self.role == 'Premium':
            return format_html(f'<span style="color: #FFBD1B;"><strong>{self.role}</strong></span>')
        else:
            return self.role

    colored_premium.short_description = 'Role'
    colored_premium.admin_order_field = 'role'

    def get_absolute_url(self):
        return reverse('siteweather:profile', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']


class WeatherDescription(models.Model):
    short_description = models.CharField(verbose_name='Main description', max_length=300, blank=True)
    full_description = models.CharField(verbose_name='Full description', max_length=300, blank=True)
    weather_icon = models.CharField(verbose_name='Icon', max_length=300, default='01d', blank=True, unique=True,
                                    primary_key=True)


class Location(models.Model):
    city_name = models.CharField(verbose_name='Name of city', max_length=300, unique=True, primary_key=True)
    country = models.CharField(verbose_name='Country', max_length=300, default='Unknown', blank=True)


class CityBlock(models.Model):
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True)
    weather_description = models.ForeignKey(WeatherDescription, on_delete=models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    temperature = models.IntegerField(verbose_name='Temperature', default=0, blank=True)
    humidity = models.IntegerField(verbose_name='Humidity', default=0, blank=True)
    pressure = models.IntegerField(verbose_name='Pressure', default=0, blank=True)
    wind_speed = models.IntegerField(verbose_name='Wind speed', default=0, blank=True)
    searched_by_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('siteweather:view_city', kwargs={'pk': self.pk})

    def __str__(self):
        return self.location.city_name

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['-timestamp']
        permissions = [
            ('see_users', 'Ability to see users from specific city in city block'),
        ]
