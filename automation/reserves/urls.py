#
from django.urls import path
from reserves import views

app_name = 'reserves'

urlpatterns = [
    path('stock/list/', views.StockList.as_view(), name='stock_list'),
    path('stock/remove/<int:pk>', views.stock_remove, name='stock_remove'),
    path('stock/create/', views.StockCreate.as_view(), name='stock_create'),
    path('stock/edit/<int:pk>', views.StockEdit.as_view(), name='stock_edit'),
    #path('stock/edit/<int:pk>', views.stock_edit, name='stock_edit'),
    path('stock/add/<int:pk>', views.stock_add, name='stock_add'),
    path('stock/order/pdf/', views.order_to_pdf, name='order_to_pdf'),
]
