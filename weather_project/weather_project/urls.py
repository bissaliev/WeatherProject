from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = "weather_app.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("weather_app.urls", namespace="weather_app")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
