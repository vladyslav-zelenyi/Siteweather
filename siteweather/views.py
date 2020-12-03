import logging
from datetime import datetime

import pytz
import requests
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from task import settings
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


# class Home(ListView):
#     model = CityBlock
#     template_name = 'siteweather/home.html'
#     context_object_name = 'cities'
#     paginate_by = 2
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

    # def queryset_filter(self):
    #     city = self.request.GET.get('city_name_filter')
    #     date = self.request.GET.get('date_filter')
    #     if self.request.user.is_anonymous:
    #         result = CityBlock.objects.all()
    #     else:
    #         result = CityBlock.objects.filter(searched_by_user=self.request.user)
    #     if city != '' and city is not None and not city.isspace():
    #         city = str(city).casefold().title().strip()
    #         result = result.filter(city_name__startswith=city)
    #     if date != '' and city is not None:
    #         date_res = datetime.strptime(date, '%Y-%m-%d')
    #         result = result.filter(
    #             timestamp__year=date_res.year,
    #             timestamp__month=date_res.month,
    #             timestamp__day=date_res.day
    #         )
    #     return result


class Home(ListAPIView):
    serializer_class = CityBlockSerializer
    queryset = CityBlock.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'siteweather/home.html'

    # def get(self, request, *args, **kwargs):
    #     cities = self.get_serializer(self.get_queryset(), many=True).data
    #     return Response({'cities': cities}, template_name=self.template_name)

    # def queryset_filter(self):
    #     city = self.request.GET.get('city_name_filter')
    #     date = self.request.GET.get('date_filter')
    #     if self.request.user.is_anonymous:
    #         serialized = self.get_serializer(self.queryset, many=True).data
    #     else:
    #         serialized = self.queryset.filter(searched_by_user=self.request.user)
    #     if city != '' and city is not None and not city.isspace():
    #         city = str(city).casefold().title().strip()
    #         serialized = serialized.filter(city_name__startswith=city)
    #     if date != '' and city is not None:
    #         date_res = datetime.strptime(date, '%Y-%m-%d')
    #         serialized = serialized.filter(
    #             timestamp__year=date_res.year,
    #             timestamp__month=date_res.month,
    #             timestamp__day=date_res.day
    #         )
    #     return serialized

    def queryset_filter(self):
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

    def list(self, request, *args, **kwargs):
        queryset = self.queryset_filter()
        page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        #     return Response({'cities': serializer.data}, template_name=self.template_name)

        serializer = self.get_serializer(page, many=True)
        return Response({'cities': serializer.data}, template_name=self.template_name)


class ViewCity(RetrieveAPIView):
    serializer_class = CityBlockSerializer
    queryset = CityBlock.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'siteweather/cityblock_detail.html'

    def get(self, request, *args, **kwargs):
        city_item = self.get_object()
        serialized = self.get_serializer(city_item).data
        if self.request.user.has_perm('siteweather.see_users'):
            users = CustomUser.objects.filter(user_city=self.request.user.user_city)
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
