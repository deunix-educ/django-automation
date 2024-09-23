#
# encoding: utf-8
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
#from django.utils.text import slugify
from django.db import models
#from django_resized import ResizedImageField
from colorfield.fields import ColorField


class Location(models.Model):
    name   = models.CharField(_("Location name"), max_length=128, null=True, blank=True)
    color  = ColorField(default='#0000FF')
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Location")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Packaging(models.Model):
    name = models.CharField(_("Packaging name"), max_length=128, null=True, blank=True)
    color = ColorField(default='#00FF00')
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Packaging")
        verbose_name_plural = _("Packagings")

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(_("Product type"), max_length=32, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Product type")
        verbose_name_plural = verbose_name


class Product(models.Model):
    type = models.ForeignKey(ProductType, verbose_name=_("Product type"), on_delete=models.CASCADE, null=True)
    name  = models.CharField(_("Product name"), max_length=128, unique=True, null=True, blank=False)
    photo = models.ImageField(_("Product image"), upload_to='product/', null=True, blank=True, default = 'product/no-image.png')
    color = ColorField(default='#F0000F')
    quantity = models.DecimalField(_("Quantity"), help_text=_("Packaging quantity"), max_digits=8, decimal_places=0, null=True, blank=True, default=1)
    unity = models.CharField(_("Unity"), help_text=_("Packaging unit"), max_length=8, null=True, blank=True, default='u')       
    alert_quantity = models.IntegerField(_("Minimum stock"), null=True, blank=True, default=2)
    quantity_order = models.DecimalField(_("Quantity order"), help_text=_("Quantity to order. 0 == no order"), max_digits=8, decimal_places=0, null=True, blank=True, default=0)
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['name', 'type__name']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def photo_tag(self):
        photo = self.photo.url
        if not self.photo:
            photo = "/static/img/no-img.png"
        return mark_safe('<img src="%s" style="width: 45px; height:45px;">' % photo)

    photo_tag.short_description = _("Product")
    photo_tag.allow_tags = True

    def __str__(self):
        return self.name


# stock of product
#
def stock_expired_product():
    return [ i.id  for i in Stock.objects.filter(stocked=True).all() if i.expired_product() ]

def stock_product_to_order():
    return [ i.id  for i in Stock.objects.filter(product__active=True).all() if i.product_to_order>0 ]


class StockQuerySet(models.QuerySet):

    def stock_by_year(self, year):
        return self.filter(created__range=[ '%s-01-01' % year, '%s-12-31'% year ])

    def alert_product(self):
        return self.filter(product__alert_quantity__gt=models.F('amount'))

    def removed_product(self):
        return self.filter(stocked=False)

    def expired_product(self):
        p = stock_expired_product()
        return self.filter(pk__in=p)

    def product_to_order(self):
        p = stock_product_to_order()
        return self.filter(pk__in=p)
    
    
class StockManager(models.Manager):
    def get_queryset(self):
        return StockQuerySet(self.model, using=self._db)

    def stock_by_year(self, year):
        return self.get_queryset().stock_by_year(year)

    def alert_product(self):
        return self.get_queryset().alert_product()

    def removed_product(self):
        return self.get_queryset().removed_product()

    def expired_product(self):
        return self.get_queryset().expired_product()

    def product_to_order(self):
        return self.get_queryset().product_to_order()
    
class Stock(models.Model):
    created = models.DateField(_("Creation date"), blank=False, null=True, editable=True)
    product = models.ForeignKey(Product, verbose_name=_("Products"), related_name='Stock_product', on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, verbose_name=_("Storage places"), related_name='Stock_location', on_delete=models.CASCADE, null=True)
    range  = models.DecimalField(_("Range"), max_digits=8, decimal_places=0, null=True, blank=True, default=1)
    packaging = models.ForeignKey(Packaging, verbose_name=_("Packagings"), on_delete=models.CASCADE, null=True)   
    expiry_date_days= models.IntegerField(_("Expiry date in days"), null=True, default=365)
    
    amount  = models.DecimalField(_("Amount"), max_digits=8, decimal_places=0, null=True, blank=True, default=1)
    stocked = models.BooleanField(_("Stocked"), default=True)
    onorder = models.BooleanField(_("On order"), default=False)
    objects = StockManager()

    class Meta:
        ordering = ['created', 'product__name', 'location__name', 'range', ]
        unique_together = ('created', 'product', 'location', 'range', 'packaging', )
        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")

    def alert_product(self):
        return self.amount < self.product.alert_quantity
    
    @property
    def product_to_order(self):
        q = self.product.quantity_order - self.amount
        if self.alert_product():
            return 0 if q <= 0 else q
        return 0
    
    def removed_product(self):
        return self.stocked == False

    def expired_product(self):
        expired_date = self.created + timedelta(days=self.expiry_date_days)
        return timezone.now().date() > expired_date
    
    @property
    def stock_amount(self):
        amount = self.amount * self.product.quantity
        return f'{amount} {self.product.unity}'
  
    #def save(self, *args, **kwargs):
    #    if not self.id:
    #        self.created = timezone.now()
    #    super().save(*args, **kwargs)
        
    def __str__(self):
        return self.product.name
#
