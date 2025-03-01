"""
URL configuration for cpgsserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.views.generic import TemplateView
from cpgsapp import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Endpoints
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('network_handler', views.NetworkHandler.as_view()),
    path('live_stream_handler', views.LiveStreamHandler.as_view()),
    path('account_handler', views.AccountHandler.as_view()),
    path('monitor_handler', views.MonitorHandler.as_view()),
    path('calibrate_handler', views.CalibrateHandler.as_view()),
    path('initiate', views.initiate),
    
    path('',TemplateView.as_view(template_name = 'index.html'))
] + staticfiles_urlpatterns()
