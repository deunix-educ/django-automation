# Register your models here.
#from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LoggedInUser, HomeSite


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'homesite', 'email', 'image_tag', 'is_active', 'is_staff', 'is_superuser', )
    list_filter  = ('is_active', 'is_staff', 'is_superuser')
    add_exclude = ('fisrt_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        (None, { 'fields': ( 'homesite', 'adr1', 'adr2', 'zip', 'city', 'mobile', 'photo', )}),
    )


    def get_form(self, request, obj=None, **kwargs):
        is_superuser = request.user.is_superuser
        if not is_superuser:
            self.exclude = ('is_staff', 'is_active', 'is_superuser', 'user_permissions',)
        form = super().get_form(request, obj, **kwargs)
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {'username', 'email', }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form



class HomeSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'adr1', 'adr2', 'zip', 'city' )

class LoggedInUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key')


admin.site.register(HomeSite, HomeSiteAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(LoggedInUser, LoggedInUserAdmin)


