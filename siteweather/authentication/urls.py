from django.urls import path, include

from .views import *


registration_urls = ([
    path('login/', UserLoginFormView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', RegisterFormView.as_view(), name='register'),
], 'auth')

urlpatterns = [
    path('auth/', include(registration_urls)),
]
