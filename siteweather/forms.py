from django import forms


class CityBlockForm(forms.Form):
    city_name = forms.CharField(max_length=300, label='City name', widget=forms.TextInput(attrs={'class': 'form-control'}))
