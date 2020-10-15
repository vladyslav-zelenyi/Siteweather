from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('siteweather/<int:pk>/', ViewCity.as_view(), name='view_city'),
    path('find_by/', FindCity.as_view(), name='find_by'),
    # path('page_filter/', city_filter, name='page_filter'),
    path('registration/', RegisterFormView.as_view(), name='registration'),
    # path('login/', UserLoginFormView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
]
