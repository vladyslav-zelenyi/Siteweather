import requests

from task import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, RedirectView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.views import View

from .models import CityBlock, CustomUser
from .forms import CityBlockForm, UserRegisterForm, UserLoginForm, UserUpdateForm, UserUpdatePasswordForm, SendMailForm


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
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
            )
            login(request, user)
            return redirect('siteweather:profile', pk=user.pk)
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
                user = CustomUser.objects.get(username=username)
                return redirect('weather:profile', pk=user.id)
        return render(request, 'registration/login.html', {'form': form})


class UserLogoutView(RedirectView):
    pattern_name = 'siteweather:home'

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('siteweather:home')


class UserProfile(DetailView):
    model = CustomUser
    context_object_name = 'profile'
    template_name = 'registration/profile.html'


class UserProfileUpdate(UpdateView):
    model = CustomUser
    context_object_name = 'profile'
    form_class = UserUpdateForm
    template_name = 'registration/update.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone_number']
            check = request.POST.get('photo-clear')
            if check == 'on':
                user.photo = None
            if check is None and form.cleaned_data['photo'] is None:
                pass
            else:
                user.photo = form.cleaned_data['photo']
            user.save()
            return redirect('siteweather:profile', pk=user.pk)
        return render(request, self.template_name, {'form': form})


class UserPasswordUpdate(UpdateView):
    model = CustomUser
    context_object_name = 'profile'
    form_class = UserUpdatePasswordForm
    template_name = 'registration/password_update.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('/', pk=user.pk)
        return render(request, self.template_name, {'form': form})


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
        try:
            city = self.request.GET.get('city_name_filter')
            date = self.request.GET.get('date_filter')
            if str(self.request.user) == 'AnonymousUser':
                result = CityBlock.objects.all()
            else:
                result = CityBlock.objects.filter(searched_by_user=self.request.user)
            if city != '' and self.request.GET.get('city_name_filter') is not None:
                result = result.filter(city_name=city)
            if date != '' and self.request.GET.get('date_filter') is not None:
                year = date[0:4]
                month = date[5:7]
                day = date[8:]
                result = result.filter(timestamp__year=year, timestamp__month=month, timestamp__day=day)
            return result
        except TypeError:
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
            if str(request.user) != 'AnonymousUser':
                city_weather['searched_by_user'] = request.user
            else:
                city_weather['searched_by_user'] = CustomUser.objects.get(pk=1)
            city = CityBlock.objects.create(**city_weather)
            return redirect(city)
        return render(request, self.template_name, {'form': form})


class SendMail(View):
    form_class = SendMailForm
    template_name = 'registration/mail.html'
    subject = 'Django'
    message = """Test message from Vlad.

Kind regards,
Vlad"""

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            send_mail(subject=self.subject, from_email=settings.EMAIL_HOST,
                      message=self.message, recipient_list=[form.cleaned_data['mail_to']])
            return redirect('weather:mail')
        return render(request, self.template_name, {'form': form})
