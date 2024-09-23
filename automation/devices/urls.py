# encoding: utf-8
#
#from django.utils.translation import gettext_lazy as _
from django.urls import path
from devices import views

app_name = 'devices'

urlpatterns = [       
    path('load/chart/<int:pid>/', views.load_chart, name='load_chart'),   
    path('graph/<str:page>/', views.graph_plotting, name='graph_plotting'),
    path('graph/plot/<int:pid>/', views.graph_plot_by_id, name='graph_plot_by_id'),
]
