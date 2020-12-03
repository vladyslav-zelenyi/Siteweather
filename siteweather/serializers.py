import re

import requests
from rest_framework import serializers

from siteweather.models import CustomUser, CityBlock
from task import settings


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


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    password2 = serializers.CharField(max_length=300, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2', 'phone_number', 'user_city']
        extra_kwargs = {
            'email': {'required': True},
            'password2': {'required': True},
            'user_city': {'required': True},
        }

    def validate_password2(self, value):
        data = self.get_initial()
        if data['password'] != value:
            raise serializers.ValidationError('The verification password does not match the entered one')
        return data

    def validate_first_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('First name is too short')
        return value

    def validate_last_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Surname is too short')
        return value

    def validate_phone_number(self, value):
        if value:
            letters_check = value[1:].isdecimal()
            symbols_check = re.search(r'\W', value[1:])
            plus_check = re.search(r'\W', value[0])
            if plus_check is not None and symbols_check is None and letters_check is True:
                if value[0] != '+':
                    raise serializers.ValidationError('Only '+' is allowed at the beginning')
            if letters_check is False or symbols_check is not None:
                raise serializers.ValidationError('Only numbers are allowed')
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with entered email exists')
        return value

    def validate_user_city(self, value):
        url = f'{settings.SITE_WEATHER_URL}?q={value}&appid={settings.APP_ID}&units=metric'
        r = requests.get(url).json()
        if r['cod'] == '404':
            raise serializers.ValidationError('City was not found')
        return value

    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError('Your value has to contain at least 4 symbols')
        if ' ' in str(value):
            raise serializers.ValidationError('No spaces allowed')
        check_username = CustomUser.objects.filter(username=value).exists()
        if check_username:
            raise serializers.ValidationError('Username is taken')
        return value
