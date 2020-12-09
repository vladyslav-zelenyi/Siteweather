from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from siteweather.views import schema_view
from task import settings
from siteweather.authentication.views import AdminLogoutView


urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view, name="docs"),
    path('admin/logout/', AdminLogoutView.as_view()),
    path('admin/', admin.site.urls),
    path('', include('siteweather.urls', namespace='siteweather')),
    path('api-auth/', include('rest_framework.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
