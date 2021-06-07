import pytz
from rest_framework import serializers

from siteweather.models import CityBlock, WeatherDescription, Location
from siteweather.authentication.serializers import RegistrationSerializer
from siteweather.profile.serializers import CustomUserSerializer


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class WeatherDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherDescription
        fields = '__all__'


class CityBlockSerializer(serializers.ModelSerializer):
    customers = CustomUserSerializer(many=True, read_only=True)
    searched_by_user = CustomUserSerializer(read_only=True)
    weather_description = WeatherDescriptionSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = CityBlock
        fields = '__all__'


class FindCityBlockSerializer(LocationSerializer, RegistrationSerializer):
    city_name = serializers.CharField(label='Name of city', max_length=300, validators=[])

    class Meta:
        model = Location
        fields = ('city_name',)

    def validate_city_name(self, city_name):
        return self.validate_user_city(city_name)


class DeleteCityBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityBlock
        fields = '__all__'
        # fields = ['pk', 'city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
        #           'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country']
        read_only_fields = fields


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
