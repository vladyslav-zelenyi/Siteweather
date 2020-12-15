import re
from datetime import datetime, date, timedelta

import pytz
import requests
from django.contrib.auth import update_session_auth_hash, authenticate
from django.core.mail import send_mail
from django.utils.timezone import now, localdate
from pytz import UnknownTimeZoneError
from rest_framework import serializers

from siteweather.authentication.utils import username_validator
from siteweather.models import CustomUser, CityBlock
from task import settings


class CustomUserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(method_name='get_age')
    is_registered_recently = serializers.SerializerMethodField(method_name='get_is_registered_recently')

    class Meta:
        model = CustomUser
        fields = ['pk', 'first_name', 'last_name', 'email', 'photo', 'phone_number', 'user_city', 'age',
                  'is_registered_recently', 'date_of_birth', 'role']

    def get_age(self, obj):
        today = date.today()
        age = today.year - obj.date_of_birth.year - ((obj.date_of_birth.month, obj.date_of_birth.day) >
                                                     (today.month, today.day))
        return age

    def get_is_registered_recently(self, obj):
        days_to_stay_marked = timedelta(days=3)
        today = localdate()
        if (today - obj.date_joined.date()) > days_to_stay_marked:
            return False
        return True


class SuperUserCustomUserSerializer(CustomUserSerializer):
    days_since_joined = serializers.SerializerMethodField(method_name='get_days_since_joined')
    user_permissions = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = CustomUser
        fields = '__all__'

    def get_days_since_joined(self, obj):
        return (now() - obj.date_joined).days


class CityBlockSerializer(serializers.ModelSerializer):
    customers = CustomUserSerializer(many=True, read_only=True)
    searched_by_user = CustomUserSerializer(read_only=True)

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
            if plus_check is not None and symbols_check is None and letters_check is True:
                if value[0] != '+':
                    raise serializers.ValidationError('Only ' + ' is allowed at the beginning')
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


class FindCityBlockSerializer(CityBlockSerializer, RegistrationSerializer):
    class Meta:
        model = CityBlock
        fields = ['city_name']

    def validate_city_name(self, city_name):
        return self.validate_user_city(city_name)


class UpdateProfileSerializer(RegistrationSerializer):
    photo_clear = serializers.BooleanField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'user_city', 'photo', 'photo_clear',
                  'date_of_birth']

    def validate_email(self, value):
        object_to_compare = CustomUser.objects.filter(email=value)
        if object_to_compare.exists() and self.instance.pk != object_to_compare[0].pk:
            raise serializers.ValidationError('User with entered email exists')
        return value

    def save(self, request, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        check = request.POST.get('photo-clear')
        if check == 'on' or request.POST.get('photo_clear') == 'true':
            validated_data['photo'] = None
            self.instance = self.update(self.instance, validated_data)
            return self.instance
        if validated_data.get('photo') is None:
            validated_data['photo'] = self.instance.photo
        self.instance = self.update(self.instance, validated_data)
        return self.instance


class UpdatePasswordSerializer(RegistrationSerializer):
    class Meta:
        model = CustomUser
        fields = ['password', 'password2']

    def save(self, request, **kwargs):
        user = request.user
        validated_data = {**self.validated_data, **kwargs}
        user.set_password(validated_data['password'])
        default_zone = settings.TIME_ZONE
        try:
            current_timezone = pytz.timezone(request.session.get('django_timezone'))
        except UnknownTimeZoneError:
            current_timezone = pytz.timezone(default_zone)
        time = datetime.now().astimezone(current_timezone)
        time = f'{time.year}-{time.month}-{time.day} | {time.hour}:{time.minute}:{time.second}'
        update_session_auth_hash(request, user)
        send_mail(
            subject='Password change',
            from_email='Siteweather',
            message=f"Your password has been changed to '{validated_data['password']}'. Time - {time}",
            recipient_list=[user.email]
        )
        user.save()


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
