from django.urls import path
from .views import *

app_name = 'siteweather'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('siteweather/<int:pk>/', ViewCity.as_view(), name='view_city'),
    path('siteweather/<int:pk>/delete_confirmation/', DeleteCityBlock.as_view(), name='delete_confirmation'),
    path('find_by/', FindCity.as_view(), name='find_by'),
    path('login/', UserLoginFormView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('registration/', RegisterFormView.as_view(), name='registration'),
    path('profile/<int:pk>/', UserProfile.as_view(), name='profile'),
    path('profile/<int:pk>/update/', UserProfileUpdate.as_view(), name='update'),
    path('profile/<int:pk>/password_update/', UserPasswordUpdate.as_view(), name='password_update'),
    path('siteweather/site_settings/', PersonalSiteSettings.as_view(), name='site_settings')
]
