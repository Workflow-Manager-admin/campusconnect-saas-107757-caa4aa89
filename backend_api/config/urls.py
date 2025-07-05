"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt

# API Schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Campus Connect API",
        default_version='v1',
        description="API for Campus Connect placement management system",
        terms_of_service="https://www.campusconnect.com/terms/",
        contact=openapi.Contact(email="contact@campusconnect.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def get_full_url(request):
    """Helper function to get the full URL including port"""
    scheme = request.scheme
    host = request.get_host()
    forwarded_port = request.META.get("HTTP_X_FORWARDED_PORT")

    if ':' not in host and forwarded_port:
        host = f"{host}:{forwarded_port}"

    return f"{scheme}://{host}"

@csrf_exempt
def dynamic_schema_view(request, *args, **kwargs):
    """Dynamic schema view that updates based on the request URL"""
    url = get_full_url(request)
    view = get_schema_view(
        openapi.Info(
            title="Campus Connect API",
            default_version='v1',
            description="Complete API documentation for Campus Connect platform",
            terms_of_service="https://www.campusconnect.com/terms/",
            contact=openapi.Contact(email="contact@campusconnect.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        url=url,
    )
    return view.with_ui('swagger', cache_timeout=0)(request)

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # API Documentation
    re_path(r'^docs/$', dynamic_schema_view, name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger\.json$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
