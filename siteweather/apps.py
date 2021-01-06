from django.apps import AppConfig


class SiteweatherConfig(AppConfig):
    name = 'siteweather'

    def ready(self):
        from .models import CityBlock, CustomUser
        from siteweather.signals import city_block_changes, custom_user_changes
