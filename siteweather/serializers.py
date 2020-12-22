import pytz
from rest_framework import serializers

from siteweather.models import CityBlock
from siteweather.authentication.serializers import RegistrationSerializer
from siteweather.profile.serializers import CustomUserSerializer


class CityBlockSerializer(serializers.ModelSerializer):
    customers = CustomUserSerializer(many=True, read_only=True)
    searched_by_user = CustomUserSerializer(read_only=True)

    class Meta:
        model = CityBlock
        fields = ['pk', 'city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
                  'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country',
                  'searched_by_user', 'customers']


class FindCityBlockSerializer(CityBlockSerializer, RegistrationSerializer):
    class Meta:
        model = CityBlock
        fields = ['city_name']

    def validate_city_name(self, city_name):
        return self.validate_user_city(city_name)


class DeleteCityBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityBlock
        fields = ['pk', 'city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
                  'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country']
        read_only_fields = ['city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
                            'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country']


class AdminDeleteCityBlockSerializer(serializers.ModelSerializer):
    customers = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = CityBlock
        fields = ['pk', 'city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
                  'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country',
                  'searched_by_user', 'customers']
        read_only_fields = ['city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
                            'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country',
                            'searched_by_user', 'customers']


timezone = pytz.common_timezones


class SiteSettingsSerializer(serializers.Serializer):
    timezone_choice = serializers.ChoiceField(timezone)
