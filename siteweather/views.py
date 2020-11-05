import pytz
import logging
import requests

from datetime import datetime

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.template import RequestContext

from task import settings
from django.views import View
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from .models import CityBlock, CustomUser
from .forms import CityBlockForm, UserRegisterForm, UserLoginForm, UserUpdateForm, UserUpdatePasswordForm

logger = logging.getLogger('django')


class RegisterFormView(View):
    form_class = UserRegisterForm
    template_name = 'registration/registration.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('siteweather:profile', pk=self.request.user.pk)
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            user_city = form.cleaned_data['city_name']
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                user_city=user_city,
                role='Standard',
            )
            group = Group.objects.get(name='Registered')
            user.groups.add(group)
            permissions = group.permissions.all()
            user.user_permissions.set(permissions)
            login(request, user)
            message = 'You have successfully registered on the site'
            logger.info(f"{username} was registered and authorized")
            send_mail(
                subject='Registration',
                from_email='Siteweather',
                message=message,
                recipient_list=[email]
            )
            return redirect('siteweather:profile', pk=user.pk)
        return render(request, self.template_name, {'form': form})


class UserLoginFormView(LoginView):
    form_class = UserLoginForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('siteweather:profile', pk=self.request.user.pk)
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                user = CustomUser.objects.get(username=username)
                logger.info(f"{username} was authorized")
                return redirect('weather:profile', pk=user.id)
        else:
            if CustomUser.objects.filter(username=form.cleaned_data['username']):
                logger.warning(f"Unsuccessful authorization into {form.cleaned_data['username']}")
        return render(request, 'registration/login.html', {'form': form})


class UserLogoutView(View):
    url = 'siteweather:home'

    def get(self, request, *args, **kwargs):
        timezone = request.session.get('django_timezone')
        logout(request)
        logger.info(f"{self.request.user.username} logged out")
        request.session['django_timezone'] = timezone
        return redirect(self.url)


class AdminLogoutView(UserLogoutView):
    url = '/admin/'


class UserProfile(DetailView):
    model = CustomUser
    context_object_name = 'profile'
    template_name = 'registration/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        return context


class UserProfileUpdate(UpdateView):
    model = CustomUser
    context_object_name = 'profile'
    form_class = UserUpdateForm
    template_name = 'registration/update.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone_number']
            user.user_city = form.cleaned_data['city_name']
            check = request.POST.get('photo-clear')
            if check == 'on':
                user.photo = None
            if check is None and form.cleaned_data['photo'] is None:
                pass
            else:
                user.photo = form.cleaned_data['photo']
            user.save()
            logger.info(f"{user} updated his profile")
            return redirect('siteweather:profile', pk=user.pk)
        return render(request, self.template_name, {'form': form})


class PersonalSiteSettings(View):
    template_name = 'siteweather/site_settings.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'timezones': pytz.common_timezones})

    def post(self, request, *args, **kwargs):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')


class UserPasswordUpdate(UpdateView):
    model = CustomUser
    context_object_name = 'profile'
    form_class = UserUpdatePasswordForm
    template_name = 'registration/password_update.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['password'])
            password = form.cleaned_data['password']
            user.save()
            logger.warning(f'{user} updated his password')
            default_zone = settings.TIME_ZONE
            current_timezone = pytz.timezone(request.session.get('django_timezone', default_zone))
            time = datetime.now().astimezone(current_timezone)
            time = f'{time.year}-{time.month}-{time.day} | {time.hour}:{time.minute}:{time.second}'
            send_mail(
                subject='Password change',
                from_email='Siteweather',
                message=f"Your password has been changed to '{password}'. Time - {time}",
                recipient_list=[user.email])
            update_session_auth_hash(request, form.user)
            return redirect('siteweather:home')
        return render(request, self.template_name, {'form': form})


class UsersList(ListView):
    model = CustomUser
    template_name = 'siteweather/registered_users.html'
    context_object_name = 'profile'
    paginate_by = 8

    def get_queryset(self):
        if self.request.user.has_perm('siteweather.see_users'):
            city = self.request.GET.get('city_name_filter')
            first_name = self.request.GET.get('first_name_filter')
            last_name = self.request.GET.get('last_name_filter')
            result = CustomUser.objects.all()
            if city != '' and city is not None and not city.isspace():
                city = str(city).casefold().title().strip()
                result = CustomUser.objects.filter(user_city__startswith=city)
            if first_name != '' and first_name is not None and not first_name.isspace():
                first_name = str(first_name).strip()
                result = result.filter(first_name__startswith=first_name)
            if last_name != '' and last_name is not None and not last_name.isspace():
                last_name = str(last_name).strip()
                result = result.filter(last_name__startswith=last_name)
            return result
        else:
            return CustomUser.objects.filter(username=self.request.user.username)


class Home(ListView):
    model = CityBlock
    template_name = 'siteweather/home.html'
    context_object_name = 'cities'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        city = self.request.GET.get('city_name_filter')
        date = self.request.GET.get('date_filter')
        if self.request.user.is_anonymous:
            result = CityBlock.objects.all()
        else:
            result = CityBlock.objects.filter(searched_by_user=self.request.user)
        if city != '' and city is not None and not city.isspace():
            city = str(city).casefold().title().strip()
            result = result.filter(city_name__startswith=city)
        if date != '' and city is not None:
            date_res = datetime.strptime(date, '%Y-%m-%d')
            result = result.filter(
                timestamp__year=date_res.year,
                timestamp__month=date_res.month,
                timestamp__day=date_res.day
            )
        return result


class ViewCity(DetailView):
    model = CityBlock
    context_object_name = 'city_item'

    def get_context_data(self, **kwargs):
        context = super(ViewCity, self).get_context_data(**kwargs)
        if self.request.user.has_perm('siteweather.see_users'):
            context['CustomUser'] = CustomUser.objects.filter(user_city=context['object'])
        return context


class DeleteCityBlock(UserPassesTestMixin, DetailView):
    model = CityBlock
    context_object_name = 'city_item'
    template_name = 'siteweather/delete_confirmation.html'

    def get(self, request, *args, **kwargs):
        return super(DeleteCityBlock, self).get(request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        block_to_delete = CityBlock.objects.filter(pk=self.kwargs['pk'])
        block_to_delete.delete()
        logger.warning(f"{self.request.user} deleted city. ID = {self.kwargs['pk']}")
        return redirect('/')

    # def handle_no_permission(self):
    #     if self.request.user.is_authenticated:
    #         raise PermissionError('Permission Denied')
    #     else:
    #         return redirect('siteweather:login')

    def test_func(self):
        block_to_delete = CityBlock.objects.get(pk=self.kwargs['pk'])
        return block_to_delete.searched_by_user == self.request.user


class FindCity(View):
    form_class = CityBlockForm
    template_name = 'siteweather/find_by.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name'].title()
            url = f'{settings.SITE_WEATHER_URL}?q={city_name}&appid={settings.APP_ID}&units=metric'
            r = requests.get(url).json()
            city_weather = {
                'city_name': r['name'],
                'weather_main_description': r['weather'][0]['main'],
                'weather_full_description': r['weather'][0]['description'],
                'weather_icon': r['weather'][0]['icon'],
                'temperature': r['main']['temp'],
                'humidity': r['main']['humidity'],
                'pressure': r['main']['pressure'],
                'wind_speed': r['wind']['speed'],
                'country': r['sys']['country'],
            }
            if self.request.user.is_authenticated:
                city_weather['searched_by_user'] = request.user
            else:
                city_weather['searched_by_user'] = CustomUser.objects.get(pk=1)
            city = CityBlock.objects.create(**city_weather)
            logger.info(f"City {city_name} was added by {self.request.user}")
            return redirect(city)
        return render(request, self.template_name, {'form': form})
