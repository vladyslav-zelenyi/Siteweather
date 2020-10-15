import requests
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.views import View

from .models import CityBlock
from .forms import CityBlockForm, UserRegisterForm, UserLoginForm


class RegisterFormView(View):
    form_class = UserRegisterForm
    template_name = 'siteweather/registration.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            login_ = form.cleaned_data['login']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user = User.objects.create_user(username=login, password=password,
                                            first_name=first_name, last_name=last_name)
            user.save()
            return redirect('/')
        return render(request, self.template_name, {'form': form})


class UserLoginFormView(View):
    form_class = UserLoginForm
    template_name = 'siteweather/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            login_field = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = authenticate(username=login_field, password=password)
            if user is not None:
                login(request, user)
                # redirect('/')
            else:
                pass
        else:
            form = UserLoginForm()
        return render(request, 'siteweather/login.html', {'form': form})


# def authenticate_user(request):
#     if request.method == 'POST':
#         form = UserLoginForm(request.POST)
#         if form.is_valid():
#             login = form.cleaned_data['login']
#             password = form.cleaned_data['password']
#             user = authenticate(username=login, password=password)
#             if user is not None:
#                 pass
#             else:
#                 pass
#     else:
#         form = UserLoginForm()
#     return render(request, 'siteweather/login.html', {'form': form})


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


class FindCity(View):
    form_class = CityBlockForm
    template_name = 'siteweather/find_by.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=21b7ad9e043e9a8fab161a49eafc3' \
                  f'27f&units=metric'
            r = requests.get(url).json()
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
        return render(request, self.template_name, {'form': form})

# def city_filter(request):
#     if request.method == 'POST':
#         form = CityBlockForm(request.POST)
#         if form.is_valid():
#             city_name = form.cleaned_data['city_name']
#             query = CityBlock.objects.raw("SELECT * FROM siteweather_cityblock WHERE city_name = %s", [city_name])
#             return render(request, 'siteweather/page_filter.html', {'query': query})
#     else:
#         form = CityBlockForm()
#     return render(request, 'siteweather/page_filter.html', {'form': form})
