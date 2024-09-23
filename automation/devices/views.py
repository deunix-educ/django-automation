# encoding: utf-8
#
import json
#from django.conf import settings
#from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from automation.views import base_context
from devices.modules.plotlib import ScatterPlot
from devices.forms import PlotForm
from devices.modules.processing import Influxdb
from devices.models import Device, Fields


def get_device(device_id):
    return Device.objects.filter(id=device_id, plot__active=True).first()

def get_field(device, dataname):
    return Fields.objects.filter(plot__id=device.plot.id, name__exact=dataname).first()
    

@login_required
@csrf_exempt
def load_chart(request, pid=None):
    if request.method == "POST":
        try:
            data = json.loads(request.body)            
            if data:
                device = get_device(pid)
                dataname = data.get('figure')
                if device and dataname:                   
                    field = get_field(device, dataname)
                    request.POST = data
                    graph = ScatterPlot(**device.plot.plotParams)                   
                    client = Influxdb(bucket=device.sensor)
                    df = client.dataframe(
                        device.sensor,
                        dataname, 
                        start=data.get('date_range', '-1m'), 
                        agg_fn=field.func, 
                        frequency=data.get('frequency'),
                        empty=field.connect_gaps
                    )                                       
                    plot = graph.simple_figure(df, figures=[field.plot_field, ], mode=data.get('mode'), interpolation=data.get('interpolation'))             
                    return JsonResponse(dict(status=True, graph=plot))
        except Exception as e:
            print("Load_chart error", e)
    return JsonResponse(dict(status=False))


################
# graph
def graph_params(device):
    graph = {}
    if device:
        Form = PlotForm(device)
        graph = dict(
            devid=device.id,
            device=device,
            form = Form(initial=Form.plotform_initial()),
            return_url = reverse('board'),      
        )
    return graph


def device_graph(request, page, device_id=None):
    device = get_device(device_id)
    return base_context(request, Device.objects.filter(plot__active=True), page, **graph_params(device))


@login_required
@xframe_options_exempt
def graph_plotting(request, page=None):
    pid = request.POST.get('devid')
    template, context = device_graph(request, page, device_id=pid)     
    return render(request, template, context=context)


@login_required
@xframe_options_exempt
def graph_plot_by_id(request, pid=None):
    device = get_device(pid)
    graph = graph_params(device)
    return render(request, 'devices/plot/plot.html', context=graph)
