from django.urls import path, include

from .views import *

app_name = 'siteweather'

siteweather_urls = [
    path('', Home.as_view(), name='home'),
    path('<int:pk>/', ViewCity.as_view(), name='view_city'),
    path('<int:pk>/delete_confirmation/', DeleteCityBlock.as_view(), name='delete_confirmation'),
    path('find_by/', FindCity.as_view(), name='find_by'),
    path('registered_users/', UsersList.as_view(), name='users_list'),
    path('site_settings/', PersonalSiteSettingsAPIView.as_view(), name='site_settings'),
]

urlpatterns = [
    path('', include('siteweather.authentication.urls')),
    path('', include('siteweather.profile.urls')),
    path('siteweather/', include(siteweather_urls)),
]
