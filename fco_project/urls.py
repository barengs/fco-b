"""
URL configuration for fco_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def redirectRoute(request):
    return redirect('api/docs/')

urlpatterns = [
    path('', redirectRoute),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/owners/', include('owners.urls')),
    path('api/ships/', include('ships.urls')),
    path('api/fish/', include('fish.urls')),
    path('api/catches/', include('catches.urls')),
    path('api/regions/', include('regions.urls')),
    path('api/admin/', include('admin_module.urls')),  # Add admin module URLs
    path('api/blockchain/', include('blockchain.urls')),  # Add blockchain module URLs
    # drf-spectacular URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]