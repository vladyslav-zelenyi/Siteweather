from django.contrib import admin

from .models import CityBlock


class CityBlockAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'weather_main_description', 'weather_full_description', 'timestamp', 'temperature', 'wind_speed', 'humidity', 'pressure')
    list_display_links = ('city_name',)
    search_fields = ('city_name', 'timestamp')
    list_filter = ('city_name', 'timestamp')


admin.site.register(CityBlock, CityBlockAdmin)
