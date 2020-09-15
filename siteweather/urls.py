from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('siteweather/<int:pk>/', ViewCity.as_view(), name='view_city'),
    path('find_by/', find_by, name='find_by'),
    path('page_filter/', city_filter, name='page_filter'),
]