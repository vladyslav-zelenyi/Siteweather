import re
from datetime import date

import requests
from django.contrib.auth import authenticate
from rest_framework import serializers

from siteweather.authentication.utils import username_validator
from siteweather.models import CustomUser
from task import settings


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    password2 = serializers.CharField(max_length=300, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2', 'phone_number', 'user_city',
                  'date_of_birth']
        extra_kwargs = {
            'email': {'required': True},
            'password2': {'required': True},
            'user_city': {'required': True},
            'date_of_birth': {'required': True},
        }

    def validate_password2(self, value):
        data = self.get_initial()
        if data['password'] != value:
            raise serializers.ValidationError('The verification password does not match the entered one')
        return data

    def validate_first_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('First name has to contain at least 2 symbols')
        return value

    def validate_last_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Surname has to contain at least 2 symbols')
        return value

    def validate_phone_number(self, value):
        if value:
            letters_check = value[1:].isdecimal()
            symbols_check = re.search(r'\W', value[1:])
            plus_check = re.search(r'\W', value[0])
            if plus_check and not symbols_check and letters_check:
                if value[0] != '+':
                    raise serializers.ValidationError('Only + is allowed at the beginning')
            if not letters_check or symbols_check:
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
        if r['cod'] == '500':
            raise serializers.ValidationError('OpenWeather server error')
        return value

    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError('Your username has to contain at least 4 symbols')
        if ' ' in str(value):
            raise serializers.ValidationError('No spaces allowed')
        check_username = CustomUser.objects.filter(username=value).exists()
        if check_username:
            raise serializers.ValidationError('Username is taken')
        return value

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError('You cannot provide a date of birth from the future')
        return value


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
    )
    password = serializers.CharField(max_length=150, required=True, )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def validate_password(self, password):
        data = self.get_initial()
        user = authenticate(username=data['username'], password=password)
        if user:
            return user
        raise serializers.ValidationError('Wrong username or password')
