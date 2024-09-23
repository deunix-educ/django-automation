#
# encoding: utf-8
#import subprocess, os
import json, logging
import paho.mqtt.publish as publish
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from celery import shared_task
from devices.models import Device

logger = logging.getLogger(__name__)

def publish_message(device, evt, **payload):
    try:
        if device:
            print(f'publish_message............: {device.basetopic}/{evt}', payload)
            publish.single(f'{device.basetopic}/{evt}', json.dumps(payload), **settings.MQTT_SINGLE)
            return True
    except Exception as e:
        logger.error(f"publish_message error {device}: {e}")
    return False    

def get_device(uuid):
    if not uuid:
        return None
    device = Device.objects.filter(uuid__exact=uuid).first()
    if device and not device.active:
        return None
    return device

@shared_task
def recording_on(uuid=None, **kwargs):
    device = get_device(uuid)
    device.record = True
    device.save()

@shared_task
def recording_off(uuid=None, **kwargs):
    device = get_device(uuid)
    device.record = False
    device.save()

@shared_task
def switch_on(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='ON')

@shared_task
def switch_off(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='OFF')

@shared_task
def switch_toggle(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='TOGGLE')


@shared_task
def relay_switch_close(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='CLOSE')

@shared_task
def relay_switch_open(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='OPEN')

@shared_task
def relay_switch_stop(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='STOP')

@shared_task
def relay_switch_toggle(uuid=None, **kwargs):
    device = get_device(uuid)
    return publish_message(device, evt='set', state='TOGGLE')


