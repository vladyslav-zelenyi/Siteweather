import logging

from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from siteweather.authentication.forms import *
from siteweather.authentication.serializers import LoginSerializer
from siteweather.serializers import RegistrationSerializer

logger = logging.getLogger('django')


class RegisterFormView(CreateAPIView):
    serializer_class = RegistrationSerializer
    template_name = 'authentication/registration.html'
    form_class = UserRegisterForm
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = None

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('siteweather:profile:profile', pk=self.request.user.pk)
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return redirect('siteweather:profile:profile', pk=self.request.user.pk)
        else:
            return Response({
                'errors': serializer.errors,
                'data': serializer.data,
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_create(self, serializer):
        user = CustomUser.objects.create_user(**serializer.data, role='Standard')
        group = Group.objects.get(name='Registered')
        user.groups.add(group)
        base_permissions = group.permissions.all()
        user.user_permissions.set(base_permissions)
        login(self.request, user)


class UserLoginFormView(GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = (MultiPartParser, FormParser)
    template_name = 'authentication/login.html'
    form_class = UserLoginForm

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('siteweather:profile:profile', pk=self.request.user.pk)
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data={'username': request.data['username'],
                                           'password': request.data['password']})
        if serializer.is_valid():
            user = serializer.validated_data['password']
            login(request, user)
            return redirect('siteweather:profile:profile', user.pk)
        else:
            user = CustomUser.objects.filter(username__exact=serializer.data['username']).exists()
            if user:
                logger.warning(f"Unsuccessful authorization into {serializer.data['username']}")
            return Response({
                'errors': serializer.errors,
                'data': serializer.data,
                }, template_name=self.template_name, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserLogoutView(APIView):
    url = 'siteweather:home'

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('siteweather:auth:login')
        timezone = request.session.get('django_timezone')
        logger.info(f"{self.request.user.username} logged out")
        logout(request)
        request.session['django_timezone'] = timezone
        return redirect(self.url)


class AdminLogoutView(UserLogoutView):
    url = '/admin/'

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
