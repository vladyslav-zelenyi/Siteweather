import logging

from django import forms

from siteweather.authentication.forms import BaseCustomUserForm

logger = logging.getLogger('django')


class CityBlockForm(BaseCustomUserForm):
    first_name = None
    last_name = None
    email = None
    phone_number = None


class CityBlockFilterForm(forms.Form):
    city_name_filter = forms.CharField(max_length=300, label='city_name_filter', widget=forms.TextInput(
        attrs={'class': 'form-control'}), )
    date_filter = forms.DateField(label='date_filter', widget=forms.DateInput(
        attrs={'class': 'form-control'}), )
