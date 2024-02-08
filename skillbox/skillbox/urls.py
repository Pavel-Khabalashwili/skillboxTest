from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('authentication/', include('authentication.urls')),
    path('register/', include('register.urls')),
]
