from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from task import settings
from siteweather.authentication.views import AdminLogoutView


schema_view = get_schema_view(
   openapi.Info(
      title="SWAGGER",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view, name="docs"),
    path('admin/logout/', AdminLogoutView.as_view()),
    path('admin/', admin.site.urls),
    path('', include('siteweather.urls', namespace='siteweather')),
    path('api-auth/', include('rest_framework.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
