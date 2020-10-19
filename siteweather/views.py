import requests

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, RedirectView, UpdateView
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views import View

from .models import CityBlock
from .forms import CityBlockForm, UserRegisterForm, UserLoginForm


class RegisterFormView(View):
    form_class = UserRegisterForm
    template_name = 'registration/registration.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            user = get_user_model().objects.create_user(
                username=username, password=password, first_name=first_name, last_name=last_name, email=email,
                phone_number=phone_number)
            user.save()
            login(request, user)
            return redirect('/')
        return render(request, self.template_name, {'form': form})


class UserLoginFormView(View):
    form_class = UserLoginForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                user = get_user_model().objects.get(username=username)
                return redirect('weather:profile', pk=user.id)
        return render(request, 'registration/login.html', {'form': form})


class UserLogoutView(RedirectView):
    pattern_name = 'siteweather:home'

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('siteweather:home')


class UserProfile(DetailView):
    model = get_user_model()
    context_object_name = 'profile'
    template_name = 'registration/profile.html'


class UserProfileUpdate(UpdateView):
    model = get_user_model()
    template_name = 'registration/update.html'
    fields = ['first_name', 'last_name', 'photo', 'email', 'phone_number']
    context_object_name = 'profile'


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
