#
# encoding: utf-8
from django.utils.translation import gettext_lazy as _
from reserves.models import Stock


def stockFilter(request):
    to_order = request.GET.get('to_order') == 'on'
    alert = request.GET.get('alert') == 'on'
    removed = request.GET.get('removed') == 'on'
    expired = request.GET.get('expired') == 'on'
    year = request.GET.get('year')
    product = request.GET.get('product')
    product_type = request.GET.get('product_type')
    location = request.GET.get('location')
    packaging = request.GET.get('packaging')

    stock = Stock.objects.filter(stocked=not removed).order_by('created')
    title = [str(_("Stock"))]
    if alert:
        stock = stock.alert_product()
        title.append(str(_("Alert product")))
        
    if to_order:
        stock = stock.product_to_order()
        title.append(str(_("Product to order")))
        
    if removed:
        stock = stock.removed_product()
        title.append(str(_("Removed product")))

    if expired:
        stock = stock.expired_product()
        title.append(str(_("Expired product")))

    if product:
        stock = stock.filter(product_id=product)
        title.append(str(_("Removed product")))
        
    if product_type:
        stock = stock.filter(product__type_id=product_type)

    if location:
        stock = stock.filter(location_id=location)

    if packaging:
        stock = stock.filter(packaging_id=packaging)

    if year:
        stock = stock.stock_by_year(year)

    return stock, ' '.join(title)



