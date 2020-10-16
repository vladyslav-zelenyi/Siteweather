from django.contrib.admin import ModelAdmin, site

from .models import CityBlock, CustomUser


class CityBlockAdmin(ModelAdmin):
    list_display = (
        'city_name', 'weather_main_description', 'weather_full_description', 'timestamp', 'temperature', 'wind_speed',
        'humidity', 'pressure')
    list_display_links = ('city_name',)
    search_fields = ('city_name', 'timestamp')
    list_filter = ('city_name', 'timestamp')


class CustomUserAdmin(ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'phone_number'
    )
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('date_joined', 'is_superuser',)


site.register(CityBlock, CityBlockAdmin)
site.register(CustomUser, CustomUserAdmin)
