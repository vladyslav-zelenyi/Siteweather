from datetime import timedelta, datetime

import pytz
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.utils.timezone import now, localtime
from pytz import UnknownTimeZoneError
from rest_framework import serializers

from siteweather.authentication.serializers import RegistrationSerializer
from siteweather.models import CustomUser
from task import settings


class CustomUserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    is_registered_recently = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'pk', 'first_name', 'last_name', 'email', 'photo', 'phone_number', 'user_city', 'age',
                  'is_registered_recently', 'date_of_birth', 'role']

    def get_age(self, obj):
        today = localtime()
        age = (today.date() - obj.date_of_birth).days // 365.25
        return int(age)

    def get_is_registered_recently(self, obj):
        days_to_stay_marked = timedelta(days=3)
        time_now = localtime()
        if (time_now - localtime(obj.date_joined)) > days_to_stay_marked:
            return False
        return True


class SuperUserCustomUserSerializer(CustomUserSerializer):
    days_since_joined = serializers.SerializerMethodField()
    user_permissions = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = CustomUser
        fields = '__all__'

    def get_days_since_joined(self, obj):
        return (now() - obj.date_joined).days


class UpdateProfileSerializer(RegistrationSerializer):
    photo_clear = serializers.BooleanField(write_only=True, required=False)

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
        if not validated_data.get('photo'):
            validated_data['photo'] = self.instance.photo
        self.instance = self.update(self.instance, validated_data)
        return self.instance


class UpdatePasswordSerializer(RegistrationSerializer):
    class Meta:
        model = CustomUser
        fields = ['pk', 'password', 'password2']
        read_only_fields = ['pk']

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
