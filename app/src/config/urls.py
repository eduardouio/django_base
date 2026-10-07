"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views.HomeTempView import HomeTempView

urlpatterns = [
    path('', HomeTempView.as_view(), name='home'),
    path('', include('accounts.urls')),
    path('system/', include('system.urls')),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = 'common.ErrorViews.server_error'
