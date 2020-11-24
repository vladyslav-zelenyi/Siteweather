from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from task import settings
from siteweather.views import AdminLogoutView

urlpatterns = [
    path('admin/logout/', AdminLogoutView.as_view()),
    path('admin/', admin.site.urls),
    path('', include('siteweather.urls', namespace='siteweather')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
