# Register your models here.
# encoding: utf-8
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (Product, Stock, Location, Packaging, ProductType)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'active',)
    
    
class PackagingAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'active',)


class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_type', 'photo_tag', 'quantity', 'unity', 'alert_quantity', 'active',)
    list_filter = ('type', )

    def get_type(self, instance):
        return instance.type.name
    get_type.short_description = _("Product type")


class StockAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('created', 'get_product', 'get_photo', 'get_location', 'get_pack', 'amount', 'expiry_date_days', 'stocked',)
    list_filter = ("created", "product", "location", 'packaging', 'product__type', 'stocked',)

    #, 'expiry_date_days', 'capacity', 'unit'
    def get_photo(self, instance):
        return instance.product.photo_tag()
    get_photo.short_description = _("Product image")

    def get_location(self, instance):
        return instance.location.name
    get_location.short_description = _("Storage places")

    def get_product(self, instance):
        return instance.product.name
    get_product.short_description = _("Product")

    def get_pack(self, instance):
        try:
            return instance.packaging.name
        except:
            return '?'
    get_pack.short_description = _("Packaging")


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Packaging, PackagingAdmin)
admin.site.register(Stock, StockAdmin)

