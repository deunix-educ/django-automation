#
# encoding: utf-8
#import requests
#import urllib.parse
import logging, json
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
#from django.http import HttpResponse    #, HttpResponseRedirect
#from django.template.loader import render_to_string
#from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt

from automation.models import NavPane
from automation.forms import ReplyFiltersForm
from devices.models import Device, Location, SensorGroup

logger = logging.getLogger(__name__)


def handler404(request, *args, **argv):
    return render(request, 'app.inc/404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, 'app.inc/500.html', status=500)

def page_index():
    pane = NavPane.objects.filter(active=True, index=True).first()
    return pane.page

def board_logout(request):
    logout(request)
    response = redirect('board')
    response.delete_cookie('django_language')
    return response

######################
#
def active_location():
    return [str(loc.id) for loc in Location.objects.filter(selection=True, active=True).all() ]


def active_group():
    return [str(group.id) for group in SensorGroup.objects.filter(selection=True, active=True).all() ]

def base_context(request, devices, page, **kwargs):
    panel = NavPane.objects.get(page__exact=page)
    return panel.template.htmlpath, dict(
        js_registry=[],
        devices=devices,
        codepage=page,
        panel=panel,
        items=NavPane.objects.filter(active=True, show=True).all(),
        **kwargs
        )
    
def get_context(request, devices, page, **kwargs):
    return base_context(
        request, 
        devices, 
        page, 
        grouped=SensorGroup.objects.filter(selection=True).all(),
        located=Location.objects.filter(selection=True).all(),
        **kwargs
    )

    
## board
def devices_by_key_board(request, page=None, group=None, location=None):
    devices = Device.objects.filter(active=True, display=True)
    group = request.POST.getlist('grouped', []) or active_group()
    location = request.POST.getlist('located', []) or active_location()
    if location:
        devices = devices.filter(location__id__in=location)        
    if group:
        devices = devices.filter(group__id__in=group)    
    return get_context(request, devices, page, group_checked=group, location_checked=location)


@login_required
@xframe_options_exempt
def board(request, page=None, group=None, location=None):
    if page is None:
        page = page_index()        
    template, context = devices_by_key_board(request, page, group, location)  
    #content = render_to_string(template, context, request)
    #return HttpResponse(content, content_type=None, status=None)
    return render(request, template, context=context)


## by pid
def device_by_key_pid(request, page=None, pid=None):
    devices = Device.objects.filter(id__exact=pid)
    return get_context(request, devices, page)


@login_required
@xframe_options_exempt
def device_by_pid(request, page='dashboard', pid=None):
    template, context = device_by_key_pid(request, page, pid)  
    return render(request, template, context=context)

# group by name
@login_required
@xframe_options_exempt
def device_by_groupname(request, page=None, group=None):
    if page is None:
        page = page_index()
    devices = Device.objects.filter(group__name__exact=group)    
    template, context = get_context(request, devices, page)
    return render(request, template, context=context)


################
## group

def device_by_group_location(request, group):
    devices = Device.objects.filter(active=True, display=True).order_by('group__name')
    if group:
        devices = devices.filter(group__name__exact=group) 
    location = request.POST.getlist('located', []) if request.method == "POST" else active_location()
    return devices.filter(location__id__in=location), location

def device_by_key_group(request, page=None, group=None):   
    devices, location = device_by_group_location(request, group)
    return get_context(
        request, 
        devices, 
        page, 
        location_checked=location or [], 
        form=ReplyFiltersForm(request.POST or None), 
        fpsrange=range(1, 201),
    )


@login_required
@xframe_options_exempt
def device_by_group(request, page=None, group=None):  
    template, context = device_by_key_group(request, page, group)
    return render(request, template, context=context)    

################
# mobile
def mobile_devices(request, page, group):  
    devices = Device.objects.filter(active=True, display=True, group__name__exact=group).order_by('group__name')
    mobiles = [device for device in devices if device.get_options.get('mobile')=='true']
    return get_context(
        request, 
        mobiles, 
        page, 
        form=ReplyFiltersForm(request.POST or None), 
        fpsrange=range(1, 201),
    )    

@login_required
@xframe_options_exempt
def mobile_by_group(request, page=None, group=None):  
    template, context = mobile_devices(request, page, group)
    return render(request, template, context=context)    


################
## location
def device_by_key_location(request, page=None, location=None):
    devices = Device.objects.filter(active=True, display=True).order_by('location__name')
    if location:
        devices = devices.filter(location__name__exact=location) 
        return get_context(request, devices, page)
    
    location = request.POST.getlist('located') if request.method == "POST" else active_location()
    return get_context(request, devices.filter(location__id__in=location), page, location_checked=location or [])


@login_required
@xframe_options_exempt
def device_by_location(request, page=None, location=None):
    template, context = device_by_key_location(request, page, location)  
    return render(request, template, context=context)        


## 
@login_required
def logs(request):
    with open(settings.LOGGING_FILE) as f:
        file_content = f.read()
        content = file_content.split('\n')
        return render(request, 'dashboard/logs.html', context={'logs': content, })


@login_required
def supervisor(request, pid=None):
    if pid:
        device = Device.objects.filter(active=True, service__isnull=False, ip__isnull=False, id=pid).first()        
        return render(request, 'dashboard/iframe-base.html', context={'device': device})
    devices = Device.objects.filter(active=True, service__isnull=False).all()
    return render(request, 'dashboard/supervisor.html', context={'devices': devices})
    

@login_required
@csrf_exempt
def mqtt_init(request):
    if request.method == "POST":
        try:
            response = dict(
                status=True,
                **settings.MQTT_CLIENT
            )
            return JsonResponse(response)
        except Exception as e:
            logger.error(f"mqtt_init: {e}")
    return JsonResponse({'status': False})


@login_required
@csrf_exempt
def mqtt_device(request):
    if request.method == "POST":
        try:
            datas = json.loads(request.body)
            uuid = datas.get('uuid')
            if uuid:        
                device = Device.objects.get(uuid__exact=uuid)               
                response = dict(
                    status=True,
                    basetopic=device.basetopic,
                )
                return JsonResponse(response)
        except Exception as e:
            logger.error(f"mqtt_device: {e}")
    return JsonResponse({'status': False})


@login_required
@csrf_exempt
def mqtt_disconnect(request):
    if request.method == "POST":
        try:
            response = dict(
                status=True,

            )
            return JsonResponse(response)
        except Exception as e:
            logger.error(f"page_disconnect: {e}")
    return JsonResponse({'status': False})


@login_required
@csrf_exempt
def mqtt_controller(request):
    if request.method == "POST":
        try:
            #datas = json.loads(request.body)
            response = {'status': True}
            return JsonResponse(response)
        except Exception as e:
            logger.error(f"controller: {e}")
    return JsonResponse({'status': False})


