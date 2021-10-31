from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_networks.urls')),
    path('users/', include('users.urls')),
    path('comments/', include('comments.urls')),
]
