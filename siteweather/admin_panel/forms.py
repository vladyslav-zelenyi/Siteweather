from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from django.utils.timezone import localtime

from siteweather.models import CustomUser


class CustomUserAdminForm(UserChangeForm):
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise forms.ValidationError('Your username has to contain at least 4 symbols')
        else:
            return username

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data['date_of_birth']
        today = localtime().date()
        if date_of_birth > today.today():
            raise forms.ValidationError('You cannot provide a date of birth from the future')
        return date_of_birth


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
