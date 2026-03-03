from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from apps.admin_site import custom_admin_site
from root import settings

urlpatterns = [
                  path('admin/', custom_admin_site.urls),
                  path('api/v1/', include('apps.urls')),
                  path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
                  path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
                  path('i18n/', include('django.conf.urls.i18n')),
                  path("ckeditor5/", include('django_ckeditor_5.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
