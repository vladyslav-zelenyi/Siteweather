from rest_framework import serializers

from siteweather.models import CustomUser, CityBlock


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['pk', 'username', 'first_name', 'last_name', 'email', 'date_joined',
                  'photo', 'phone_number', 'user_city', 'role']


class CityBlockSerializer(serializers.ModelSerializer):
    customers = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = CityBlock
        fields = ['pk', 'city_name', 'weather_main_description', 'weather_full_description', 'timestamp',
                  'temperature', 'weather_icon', 'humidity', 'pressure', 'wind_speed', 'country',
                  'searched_by_user', 'customers']
