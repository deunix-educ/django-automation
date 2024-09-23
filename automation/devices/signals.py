'''
Created on 24 déc. 2020

@author: denis
'''
import logging, json
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import paho.mqtt.publish as mqtt_publish

from .models import Device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Device)
def update_device(sender, instance, created, **kwargs):  # @UnusedVariable
    if created:
        instance.set_model_template(model='box', js='js')
        instance.set_model_template(model='list', js='js')

    mqtt_publish.single(
        f'{instance.basetopic}/rec/save',
        json.dumps({'record': instance.record}),
        **settings.MQTT_SINGLE
    )
    