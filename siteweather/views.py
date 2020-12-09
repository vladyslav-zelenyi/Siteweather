import logging
from datetime import datetime

import pytz
import requests
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.base import View
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import permissions, status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from task import settings
from .api_paginators import RegisteredUsersPagination
from .forms import CityBlockForm
from .models import CityBlock, CustomUser
from .serializers import CityBlockSerializer, CustomUserSerializer

logger = logging.getLogger('django')


class PersonalSiteSettings(View):
    template_name = 'siteweather/site_settings.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'timezones': pytz.common_timezones})

    def post(self, request, *args, **kwargs):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('siteweather:home')


class UsersList(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'siteweather/registered_users.html'
    pagination_class = RegisteredUsersPagination

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('city_name_filter', in_=openapi.IN_QUERY, description='City name', type=openapi.TYPE_STRING),
            Parameter('first_name_filter', in_=openapi.IN_QUERY, description='First name', type=openapi.TYPE_STRING),
            Parameter('last_name_filter', in_=openapi.IN_QUERY, description='Last name', type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        if request.user.has_perm('siteweather.see_users'):
            return self.list(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        city = self.request.GET.get('city_name_filter')
        first_name = self.request.GET.get('first_name_filter')
        last_name = self.request.GET.get('last_name_filter')
        result = CustomUser.objects.all()
        if city and not city.isspace():
            city = str(city).casefold().title().strip()
            result = CustomUser.objects.filter(user_city__startswith=city)
        if first_name and not first_name.isspace():
            first_name = str(first_name).strip()
            result = result.filter(first_name__startswith=first_name)
        if last_name and not last_name.isspace():
            last_name = str(last_name).strip()
            result = result.filter(last_name__startswith=last_name)
        return result


class Home(ListAPIView):
    serializer_class = CityBlockSerializer
    queryset = CityBlock.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'siteweather/home.html'

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('city_name_filter', in_=openapi.IN_QUERY, description='city name', type=openapi.TYPE_STRING),
            Parameter('date_filter', in_=openapi.IN_QUERY, description='date', type=openapi.FORMAT_DATE)
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        city = self.request.GET.get('city_name_filter')
        date = self.request.GET.get('date_filter')
        if self.request.user.is_anonymous:
            result = CityBlock.objects.all()
        else:
            result = CityBlock.objects.filter(searched_by_user=self.request.user)
        if city and not city.isspace():
            city = str(city).casefold().title().strip()
            result = result.filter(city_name__startswith=city)
        if date:
            date_res = datetime.strptime(date, '%Y-%m-%d')
            result = result.filter(
                timestamp__year=date_res.year,
                timestamp__month=date_res.month,
                timestamp__day=date_res.day
            )
        return result


class ViewCity(RetrieveAPIView):
    serializer_class = CityBlockSerializer
    queryset = CityBlock.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'siteweather/cityblock_detail.html'

    def get(self, request, *args, **kwargs):
        city_item = self.get_object()
        serialized = self.get_serializer(city_item).data
        if self.request.user.has_perm('siteweather.see_users'):
            users = CustomUser.objects.filter(user_city=city_item.city_name)
            user_serializer = CustomUserSerializer(users, many=True).data
            serialized['customers'] = user_serializer
        if serialized['searched_by_user'] == request.user.pk or self.request.user.is_superuser:
            serialized['permission'] = True
        return Response({'city_item': serialized}, template_name=self.template_name)


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

    def test_func(self):
        block_to_delete = CityBlock.objects.get(pk=self.kwargs['pk'])
        return block_to_delete.searched_by_user == self.request.user or self.request.user.is_superuser

    def handle_no_permission(self):
        return render(request=self.request, template_name='403.html')


class FindCity(View):
    form_class = CityBlockForm
    template_name = 'siteweather/find_by.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['user_city'].title()
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


schema_view = get_schema_view(
   openapi.Info(
      title="SWAGGER",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
