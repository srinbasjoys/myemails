from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('center_app.urls')),
    path('api/', include('email_verifier.urls')),
    path('api/', include('bulk_email_verifier.urls')),
    path('api/', include('email_finder.urls')),
    path('api/', include('new_bulk_finder.urls')),
    
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)