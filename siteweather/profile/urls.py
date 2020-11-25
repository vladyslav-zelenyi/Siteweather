from django.urls import path, include

from .views import *


profile_urls = ([
    path('<int:pk>/', UserProfile.as_view(), name='profile'),
    path('update/', UserProfileUpdate.as_view(), name='profile_update'),
    path('password_update/', UserPasswordUpdate.as_view(), name='password_update'),
], 'profile')

urlpatterns = [
    path('profile/', include(profile_urls)),
]
