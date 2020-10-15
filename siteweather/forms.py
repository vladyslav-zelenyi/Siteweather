from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# from .models import CustomUser
from django.core.exceptions import ValidationError


class CityBlockForm(forms.Form):
    city_name = forms.CharField(max_length=300, label='City name', widget=forms.TextInput(attrs={'class': 'form-control'
                                                                                                 }))


class UserRegisterForm(forms.Form):
    login = forms.CharField(max_length=300, label='login', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(attrs={'class':
                                                                                                       'form-control'}))
    password2 = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(attrs={'class':
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
        if len(str(data.get('login'))) < 5:
            self.add_error('login', 'Your login has to contain at least 5 symbols')
        if ' ' in str(data.get('login')):
            self.add_error('login', 'No spaces allowed')
        if len(str(data.get('first_name'))) < 2:
            self.add_error('first_name', 'First name error')
        if len(str(data.get('last_name'))) < 2:
            self.add_error('last_name', 'Surname error')
        return data


class UserLoginForm(forms.Form):
    login = forms.CharField(max_length=300, label='login', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=300, label='password', widget=forms.PasswordInput(attrs={'class':
                                                                                                       'form-control'}))


# class CustomUserCreationForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = CustomUser
#         fields = ('image', 'phone_number')
#
#     def clean(self):
#         data = self.cleaned_data
#         if data.get('phone_number'):
#             try:
#                 number = int(data.get('phone_number')[1:])
#             except ValueError:
#                 self.add_error('phone_number', 'Must be Integer')
#         return data
