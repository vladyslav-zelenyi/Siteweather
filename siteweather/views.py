import requests

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import CityBlock
from .forms import CityBlockForm


class Home(ListView):
    model = CityBlock
    template_name = 'siteweather/home.html'
    context_object_name = 'cities'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'List'
        return context

    def get_queryset(self):
        return CityBlock.objects.all()


class ViewCity(DetailView):
    model = CityBlock
    context_object_name = 'city_item'


def find_by(request):
    if request.method == 'POST':
        form = CityBlockForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=21b7ad9e043e9a8fab161a49eafc3' \
                  f'27f&units=metric'

            r = requests.get(url).json()
            if 'message' in r:
                form = CityBlockForm()
                return render(request, 'siteweather/not_found.html', {'form': form})
            else:
                city_weather = {
                    'city_name': city_name,
                    'weather_main_description': r['weather'][0]['main'],
                    'weather_full_description': r['weather'][0]['description'],
                    'weather_icon': r['weather'][0]['icon'],
                    'temperature': r['main']['temp'],
                    'humidity': r['main']['humidity'],
                    'pressure': r['main']['pressure'],
                    'wind_speed': r['wind']['speed'],
                    'country': r['sys']['country'],
                }
                city = CityBlock.objects.create(**city_weather)
                return redirect(city)
    else:
        form = CityBlockForm()
    return render(request, 'siteweather/find_by.html', {'form': form})


def city_filter(request):
    if request.method == 'POST':
        form = CityBlockForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            query = CityBlock.objects.raw("SELECT * FROM siteweather_cityblock WHERE city_name = %s", [city_name])
            return render(request, 'siteweather/page_filter.html', {'query': query})
    else:
        form = CityBlockForm()
    return render(request, 'siteweather/page_filter.html', {'form': form})
