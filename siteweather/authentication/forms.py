import re

import requests
from django import forms
from django.contrib.auth import authenticate

from siteweather.models import CustomUser
from task import settings


class BaseCustomUserForm(forms.Form):
    first_name = forms.CharField(max_length=300, label='first_name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=300, label='last_name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(label='email_field', widget=forms.EmailInput(
        attrs={'class': 'form-control'}), required=True)
    phone_number = forms.CharField(label='phone_number', max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=False)
    user_city = forms.CharField(max_length=300, label='user_city', widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) < 2:
            self.add_error('first_name', 'First name is too short')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 2:
            self.add_error('last_name', 'Surname is too short')
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if phone_number:
            letters_check = phone_number[1:].isdecimal()
            symbols_check = re.search(r'\W', phone_number[1:])
            plus_check = re.search(r'\W', phone_number[0])
            if plus_check is not None and symbols_check is None and letters_check is True:
                if phone_number[0] != '+':
                    self.add_error('phone_number', "Only '+' is allowed at the beginning")
            if letters_check is False or symbols_check is not None:
                self.add_error('phone_number', 'Only numbers are allowed')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if not self.user.is_anonymous:
            if self.user.email != email:
                if CustomUser.objects.filter(email=email).exists():
                    self.add_error('email', 'User with entered email exists')
        else:
            if CustomUser.objects.filter(email=email).exists():
                self.add_error('email', 'User with entered email exists')
        return email

    def clean_user_city(self):
        user_city = self.cleaned_data['user_city']
        url = f'{settings.SITE_WEATHER_URL}?q={user_city}&appid={settings.APP_ID}&units=metric'
        r = requests.get(url).json()
        if r['cod'] == '404':
            self.add_error('user_city', f'City was not found')
        return user_city


class UserRegisterForm(BaseCustomUserForm):
    username = forms.CharField(max_length=300, label='login', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(max_length=300, label='password2', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            self.add_error('password2', 'The verification password does not match the entered one')
        return data

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            self.add_error('username', 'Your username has to contain at least 4 symbols')
        if ' ' in str(username):
            self.add_error('username', 'No spaces allowed')
        check_username = CustomUser.objects.filter(username=username).exists()
        if check_username:
            self.add_error('username', 'Username is taken')
        return username


class UserLoginForm(UserRegisterForm):
    email = None
    password2 = None
    phone_number = None
    first_name = None
    last_name = None
    user_city = None

    def clean_username(self):
        return self.cleaned_data['username']

    def clean(self):
        data = self.cleaned_data
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            self.add_error('password', 'Wrong username or password')
        return data
