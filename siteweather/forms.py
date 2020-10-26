import re
import requests
import logging

from django import forms
from django.contrib.auth import authenticate

from task import settings
from .models import CustomUser
from siteweather import models

logger = logging.getLogger('django')


class CityBlockForm(forms.Form):
    city_name = forms.CharField(max_length=300, label='City name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    def clean(self):
        data = self.cleaned_data
        city_name = data.get('city_name')
        try:
            url = f'{settings.SITE_WEATHER_URL}?q={city_name}&appid={settings.APP_ID}&units=metric'
            r = requests.get(url).json()
            city_weather = {
                'weather_main_description': r['weather'][0]['main']
            }
        except KeyError:
            self.add_error('city_name', f'City {city_name} was not found')
        return data


class BaseCustomUserForm(CityBlockForm):
    first_name = forms.CharField(max_length=300, label='first_name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=300, label='last_name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(label='email_field', widget=forms.EmailInput(
        attrs={'class': 'form-control'}), required=True)
    phone_number = forms.CharField(label='phone_number', max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        super(BaseCustomUserForm, self).clean()
        data = self.cleaned_data
        if len(data.get('first_name')) < 2:
            self.add_error('first_name', 'First name is too short')
        if len(data.get('last_name')) < 2:
            self.add_error('last_name', 'Surname is too short')
        if data.get('phone_number'):
            letters_check = (data.get('phone_number'))[1:].isdecimal()
            symbols_check = re.search(r'\W', data.get('phone_number')[1:])
            plus_check = re.search(r'\W', data.get('phone_number')[0])
            if plus_check is not None and symbols_check is None and letters_check is True:
                if data.get('phone_number')[0] != '+':
                    self.add_error('phone_number', "Only '+' is allowed at the beginning")
            if letters_check is False or symbols_check is not None:
                self.add_error('phone_number', 'Only numbers are allowed')
        if not self.user.is_anonymous:
            if self.user.email != data.get('email'):
                if CustomUser.objects.filter(email=data.get('email')):
                    self.add_error('email', 'User with entered email exists')
        else:
            if CustomUser.objects.filter(email=data.get('email')):
                self.add_error('email', 'User with entered email exists')
        return data


class UserRegisterForm(BaseCustomUserForm):
    username = forms.CharField(max_length=300, label='login', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(max_length=300, label='password2', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))

    def clean(self):
        super(UserRegisterForm, self).clean()
        data = self.cleaned_data
        if data.get('password') != data.get('password2'):
            self.add_error('password2', 'The verification password does not match the entered one')
        if len(data.get('username')) < 4:
            self.add_error('username', 'Your username has to contain at least 4 symbols')
        if ' ' in str(data.get('username')):
            self.add_error('username', 'No spaces allowed')
        check_username = models.CustomUser.objects.filter(username=data.get('username')).first()
        if check_username:
            self.add_error('username', 'Username is taken')
        return data


class UserLoginForm(UserRegisterForm):
    email = None
    password2 = None
    phone_number = None
    first_name = None
    last_name = None
    city_name = None

    def clean(self):
        data = self.cleaned_data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            self.add_error('password', 'Wrong username or password')
        return data


class UserUpdateForm(BaseCustomUserForm):
    photo = forms.ImageField(label='photo', widget=forms.FileInput(
        attrs={'class': 'form-control'}), required=False, )


class UserUpdatePasswordForm(UserRegisterForm):
    email = None
    phone_number = None
    first_name = None
    last_name = None
    username = None
    city_name = None

    def clean(self):
        data = self.cleaned_data
        if data.get('password') != data.get('password2'):
            self.add_error('password2', 'The verification password does not match the entered one')
        elif self.user.check_password(data.get('password')):
            self.add_error('password2', 'You cannot change the password to the same')
        return data


class CityBlockFilterForm(forms.Form):
    city_name_filter = forms.CharField(max_length=300, label='city_name_filter', widget=forms.TextInput(
        attrs={'class': 'form-control'}),)
    date_filter = forms.DateField(label='date_filter', widget=forms.DateInput(
        attrs={'class': 'form-control'}),)
