import re

from django import forms
from django.contrib.auth import authenticate, get_user_model

from django.core.exceptions import ObjectDoesNotExist


class CityBlockForm(forms.Form):
    city_name = forms.CharField(max_length=300, label='City name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=300, label='login', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(max_length=300, label='password2', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=300, label='first_name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=300, label='last_name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(label='email_field', widget=forms.EmailInput(
        attrs={'class': 'form-control'}), required=False)
    phone_number = forms.CharField(label='phone_number', max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=False)

    def clean(self):
        data = self.cleaned_data
        if data.get('password') != data.get('password2'):
            self.add_error('password2', 'The verification password does not match the entered one')
        if len(str(data.get('username'))) < 4:
            self.add_error('username', 'Your username has to contain at least 4 symbols')
        if ' ' in str(data.get('username')):
            self.add_error('username', 'No spaces allowed')
        if len(str(data.get('first_name'))) < 2:
            self.add_error('first_name', 'First name error')
        if len(str(data.get('last_name'))) < 2:
            self.add_error('last_name', 'Surname error')
        try:
            check_username = get_user_model().objects.get(username=data.get('username'))
            if check_username:
                self.add_error('username', 'Username is taken')
        except ObjectDoesNotExist:
            pass
        if (len(str(data.get('phone_number')))) > 0:
            letters_check = (data.get('phone_number'))[1:].isdecimal()
            symbols_check = re.search(r'\W', data.get('phone_number')[1:])
            plus_check = re.search(r'\W', data.get('phone_number')[0])
            print(plus_check)
            print(data.get('phone_number')[0])
            if plus_check is not None and symbols_check is None and letters_check is True:
                if data.get('phone_number')[0] != '+':
                    self.add_error('phone_number', "Only '+' is allowed at the beginning")
            if letters_check is False or symbols_check is not None:
                self.add_error('phone_number', 'Only numbers are allowed')
        return data


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=300, label='username', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))

    def clean(self):
        data = self.cleaned_data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            self.add_error('password', 'Wrong username or password')
        return data

