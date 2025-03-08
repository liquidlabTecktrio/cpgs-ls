
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from cpgsapp import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Endpoints
urlpatterns = [
    path('admin/', admin.site.urls),
    path('network_handler', views.NetworkHandler.as_view()),
    path('account_handler', views.AccountHandler.as_view()),
    path('monitor_handler', views.MonitorHandler.as_view()),
    path('calibrate_handler', views.CalibrateHandler.as_view()),
    path('mode_handler', views.ModeHandler.as_view()),
    path('initiate', views.initiate),
    
    path('',TemplateView.as_view(template_name = 'index.html'))
] + staticfiles_urlpatterns()
