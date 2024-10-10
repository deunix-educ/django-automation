"""
URL configuration for automation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.generic import RedirectView
#from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve  
from . import views

handler404 = views.handler404
handler500 = views.handler500

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('mqtt_controller/', views.mqtt_controller, name='mqtt_controller'),
    path('mqtt/init/', views.mqtt_init, name='mqtt_init'),
    path('mqtt/device/', views.mqtt_device, name='mqtt_device'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'),name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('board/logout/', views.board_logout, name='board_logout'),
    path('', RedirectView.as_view(url='/board/', permanent=True)),   
    path('board/', views.board, name='board'),
    path('board/<str:page>/', views.board, name='board'),
    path('board/<str:page>/<str:group>/<str:location>/', views.board, name='board'),
    path('board/<str:page>/<int:pid>/', views.device_by_pid, name='device_by_pid'),

    path('group/<str:page>/', views.device_by_group, name='device_by_group'),
    path('group/<str:page>/<str:group>/', views.device_by_group, name='device_by_group'),
    path('groupname/<str:page>/<str:group>/', views.device_by_groupname, name='device_by_groupname'),
    
    path('mobile/<str:page>/', views.mobile_by_group, name='mobile_by_group'),
    path('mobile/<str:page>/<str:group>/', views.mobile_by_group, name='mobile_by_group'),

    path('locate/<str:page>/', views.device_by_location, name='device_by_location'),
    path('locate/<str:page>/<str:location>/', views.device_by_location, name='device_by_location'),
    
    path('supervisor/', views.supervisor, name='supervisor'),
    path('supervisor/<int:pid>/', views.supervisor, name='supervisor'),
    path('logs/', views.logs, name='logs'),
    
    path('devices/', include('devices.urls')),
    path('reserves/', include('reserves.urls')),
    #path('users/', include('users.urls')),
)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += i18n_patterns(
        re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    )

