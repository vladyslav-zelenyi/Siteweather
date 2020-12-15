import logging

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group

from siteweather.authentication.forms import BaseCustomUserForm
from siteweather.models import CustomUser

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
