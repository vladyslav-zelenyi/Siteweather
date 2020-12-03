import logging
from datetime import datetime

import pytz
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response


from siteweather.forms import UserUpdateForm, UserUpdatePasswordForm
from siteweather.models import CustomUser
from siteweather.serializers import CustomUserSerializer
from task import settings

logger = logging.getLogger('django')


class UserProfile(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'profile/profile.html'

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serialized = self.get_serializer(profile).data
        return Response({'profile': serialized}, template_name='profile/profile.html')


class UserProfileUpdate(UpdateView):
    model = CustomUser
    context_object_name = 'profile'
    form_class = UserUpdateForm
    template_name = 'profile/profile_update.html'

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
            return redirect('siteweather:profile:profile', pk=user.pk)
        return render(request, self.template_name, {'form': form})


class UserPasswordUpdate(UpdateView):
    model = CustomUser
    context_object_name = 'profile'
    form_class = UserUpdatePasswordForm
    template_name = 'profile/password_update.html'

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
            update_session_auth_hash(request, form.user)
            send_mail(
                subject='Password change',
                from_email='Siteweather',
                message=f"Your password has been changed to '{password}'. Time - {time}",
                recipient_list=[user.email])
            return redirect('siteweather:home')
        return render(request, self.template_name, {'form': form})
