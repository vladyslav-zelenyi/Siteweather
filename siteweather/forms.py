import logging

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group

from siteweather.authentication.forms import BaseCustomUserForm, UserRegisterForm
from siteweather.models import CustomUser

logger = logging.getLogger('django')


class CityBlockForm(BaseCustomUserForm):
    first_name = None
    last_name = None
    email = None
    phone_number = None


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

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            self.add_error('password2', 'The verification password does not match the entered one')
        elif self.user.check_password(data['password']):
            self.add_error('password2', 'You cannot change the password to the same')
        return data


class CityBlockFilterForm(forms.Form):
    city_name_filter = forms.CharField(max_length=300, label='city_name_filter', widget=forms.TextInput(
        attrs={'class': 'form-control'}), )
    date_filter = forms.DateField(label='date_filter', widget=forms.DateInput(
        attrs={'class': 'form-control'}), )


class GroupAdminForm(forms.ModelForm):

    class Meta:
        model = Group
        exclude = []

    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        self.save_m2m()
        return instance
