
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from .models import NavPane, Icon, SshTunnel, TemplatePage, SensorGroup, Location, UrlBase, Application


class IconAdmin(admin.ModelAdmin):
    list_display = ('label', 'html', )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'96'})},
    }


class NavPaneAdmin(admin.ModelAdmin):
    list_display = ('label', 'page', 'index', 'link', 'url', 'template', 'order', 'show', 'tab', 'active')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'64'})},
    }
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('link', )


class SshTunnelAdmin(admin.ModelAdmin):
    list_display = ('label', 'host', 'port', 'remote_bind_host', 'remote_bind_port', 'local_bind_host', 'local_bind_port')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'96'})},
    }


class TemplatePageAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'htmlpath', 'app', 'path', 'active',)
    list_filter = ('app__name', )

    def path(self, instance):
        if instance and instance.app:
            return instance.app.path
    path.short_description = _("Template pathname")
        
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('htmlpath', )


class SensorGroupAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'title', 'selection', 'active')
    

class LocationAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'flat',  'selection', 'active', )


class UrlBaseAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'title', 'active', )

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'path', 'is_app' )


admin.site.register(Location, LocationAdmin)
admin.site.register(SensorGroup, SensorGroupAdmin)   
admin.site.register(TemplatePage, TemplatePageAdmin)
admin.site.register(SshTunnel, SshTunnelAdmin)
admin.site.register(Icon, IconAdmin)
admin.site.register(NavPane, NavPaneAdmin)
admin.site.register(UrlBase, UrlBaseAdmin)
admin.site.register(Application, ApplicationAdmin)
