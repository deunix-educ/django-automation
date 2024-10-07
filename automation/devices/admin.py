#
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.db import models
from django import forms 


from .models import (
    Device, TopicSubscription, PeriodicTaskDevice, 
    DeviceProcessing, DeviceLinked,
    Plot, Fields, Unit, ModuleClass
)
  
    
class PeriodicTaskDeviceAdmin(admin.TabularInline):
    model = PeriodicTaskDevice
    extra = 0


class TopicSubscriptionAdmin(admin.TabularInline):
    model = TopicSubscription
    extra = 0


class DeviceLinkedAdmin(admin.TabularInline):
    model = DeviceLinked
    fk_name = 'device'
    extra = 0


class FieldsTabAdmin(admin.TabularInline):
    model = Fields
    extra = 0


class DeviceAdmin(admin.ModelAdmin):
    inlines = (DeviceLinkedAdmin, PeriodicTaskDeviceAdmin, TopicSubscriptionAdmin, )
    #list_filter = ("group", )
    list_display = ( 'uuid', '_image_tag', 'name', 'sensor', 'location', '_group', 'display', 'record', 'active')
    list_filter = ('location', 'group', 'sensor', 'active', )
    
    def _group(self, instance):
        if instance.group:
            return instance.group.name
    _group.short_description = _("Sensor group")

    def _image_tag(self, instance):
        if instance:
            return instance.image_tag()
    _image_tag.short_description = _("Device image")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('org', 'uuid', 'basetopic', )
        return self.readonly_fields


class ModuleClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'class_module')   
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'64'})},
    }


class DeviceProcessingAdmin(admin.ModelAdmin):
    list_display = ('device', 'mod_description', 'module', 'active')
    
    def mod_description(self, instance):
        if instance.module:
            return instance.module.description
    mod_description.short_description = _("Description")
    

class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')

    
class PlotAdmin(admin.ModelAdmin):

    inlines = (FieldsTabAdmin, )
    list_display = ('title', 'xtitle', 'figure', 'active',)


class FieldsAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'unit', 'metric', 'func', 'plot',)
    list_filter = ('plot', )
    
   
admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceProcessing, DeviceProcessingAdmin)
admin.site.register(ModuleClass, ModuleClassAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Plot, PlotAdmin)
admin.site.register(Fields, FieldsAdmin)




