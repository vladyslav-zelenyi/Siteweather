from django.urls import path
from .views import *

app_name = 'siteweather'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('siteweather/<int:pk>/', ViewCity.as_view(), name='view_city'),
    path('find_by/', FindCity.as_view(), name='find_by'),
    path('login/', UserLoginFormView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('registration/', RegisterFormView.as_view(), name='registration'),
    path('profile/<int:pk>/', UserProfile.as_view(), name='profile'),
]
