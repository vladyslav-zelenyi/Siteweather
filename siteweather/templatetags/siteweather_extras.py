import datetime

from django import template

from siteweather.models import CustomUser, CityBlock
from dateutil.parser import parse

register = template.Library()


@register.simple_tag
def searched_counter(city_name, request):
    count = CityBlock.objects.filter(city_name=city_name, searched_by_user=request.user.id).count()
    return {'count': count}


@register.inclusion_tag('inc/_last_registered_users.html')
def last_registered_users(count):
    last_users = CustomUser.objects.order_by('-date_joined')[:count]
    return {'last_users': last_users}


@register.filter
def correct_name(city_name):
    city_name = str(city_name).casefold().title().strip()
    return city_name


@register.filter
def parse_time(time):
    return parse(time)
