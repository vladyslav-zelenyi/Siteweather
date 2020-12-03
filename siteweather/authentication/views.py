import logging

from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.generic.base import View

from siteweather.authentication.forms import *

logger = logging.getLogger('django')


class RegisterFormView(View):
    form_class = UserRegisterForm
    template_name = 'authentication/registration.html'

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
            return redirect('siteweather:profile:profile', pk=user.pk)
        return render(request, self.template_name, {'form': form})


class UserLoginFormView(LoginView):
    form_class = UserLoginForm
    template_name = 'authentication/login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('siteweather:profile:profile', pk=self.request.user.pk)
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
                return redirect('siteweather:profile:profile', pk=user.id)
        else:
            if CustomUser.objects.filter(username=form.cleaned_data['username']):
                logger.warning(f"Unsuccessful authorization into {form.cleaned_data['username']}")
        return render(request, self.template_name, {'form': form})


class UserLogoutView(View):
    url = 'siteweather:home'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('siteweather:auth:login')
        timezone = request.session.get('django_timezone')
        logger.info(f"{self.request.user.username} logged out")
        logout(request)
        request.session['django_timezone'] = timezone
        return redirect(self.url)


class AdminLogoutView(UserLogoutView):
    url = '/admin/'
