from django.contrib import admin
from django.urls import path, include
from core import urls as core_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(core_urls)),
]