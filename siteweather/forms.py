from django import forms
from django.contrib.auth import authenticate

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class CityBlockForm(forms.Form):
    city_name = forms.CharField(max_length=300, label='City name', widget=forms.TextInput(attrs={'class': 'form-control'
                                                                                                 }))


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=300, label='login', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(attrs={'class':
                                                                                                       'form-control'}))
    password2 = forms.CharField(max_length=300, label='password2', widget=forms.PasswordInput(attrs={'class':
                                                                                                         'form-control'}))
    first_name = forms.CharField(max_length=300, label='first_name', widget=forms.TextInput(attrs={'class':
                                                                                                       'form-control'}))
    last_name = forms.CharField(max_length=300, label='last_name', widget=forms.TextInput(attrs={'class':
                                                                                                     'form-control'}))
    profile_picture = forms.ImageField(required=False)

    def clean(self):
        data = self.cleaned_data
        if data.get('password') != data.get('password2'):
            self.add_error('password2', 'The verification password does not match the entered one')
        if len(str(data.get('username'))) < 5:
            self.add_error('username', 'Your username has to contain at least 5 symbols')
        if ' ' in str(data.get('username')):
            self.add_error('username', 'No spaces allowed')
        if len(str(data.get('first_name'))) < 2:
            self.add_error('first_name', 'First name error')
        if len(str(data.get('last_name'))) < 2:
            self.add_error('last_name', 'Surname error')
        try:
            check_username = User.objects.get(username=data.get('username'))
            if check_username:
                self.add_error('username', 'Username is taken')
        except ObjectDoesNotExist:
            pass
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
