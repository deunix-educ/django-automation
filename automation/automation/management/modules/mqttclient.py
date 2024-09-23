'''
Created on 5 janv. 2023

@author: denis
'''
import json
import logging, threading
from django.conf import settings
from django.utils.text import slugify
from contrib import utils
from contrib.mqttc import MqttBase
from devices.models import Device, DeviceLinked, DeviceProcessing


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Topic(utils.TopicBase):
    topickeys = settings.MQTT_TOPIC_ARGS
    

class Processing:
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def registry(self):
        reg = {}
        for proc in DeviceProcessing.objects.filter(active=True).all():
            links = DeviceLinked.objects.filter(device=proc.device).all()            
            instance = utils.get_instance_class(proc.class_module)
            reg[proc.device.uuid] = instance(self.parent, proc.device, links)
        return reg   


class MqttWorker(MqttBase):

    def __init__(self, **p):
        super().__init__(**p)
        self.org = p.get('org')
        self.gw = p.get('gw')
        self.device_registry = {}
        self.processus = Processing(parent=self).registry()


    def mqtt_publish(self, topic, **payload):
        self._publish_message(topic, **payload)
        
        
    def mqtt_publish_bytes(self, topic, payload):
        self._publish_bytes(topic, payload)
        
                
    def publish_to_client(self, evt, **payload):
        self.mqtt_publish(f'{self.topic_base}/{evt}', **payload)


    def _on_log(self, mqttc, obj, level, string):
        """
        if string.endswith('PINGRESP'):
            logger.info(f"{mqttc.host}:{mqttc.port} is alive")
        """


    def _on_stop_mqtt(self):
        self.publish_to_client('stop', master=False)
        logger.info(f'WAITING 1s for last message')
        threading.Event().wait(1)


    def _on_connect_info(self, info):
        logger.info(f"{info}\n    subs: {self.subscriptions}")
        #self.publish_to_client('registry', master=True)


    ## registration
    #
    def unregister(self, uuid):  # @UnusedVariable
        self.device_registry.pop(uuid, None)


    def devices_data(self, org, uuid, payload):
        try:
            Device.objects.get(uuid__exact=uuid)
            #logger.info(f'{org}: Device {uuid} exist, pass!')
        except:
            try:
                Device.objects.create(**payload)
                logger.info(f'Device registration {uuid} done')
            except Exception as e:
                raise Exception(f"Device creation error: {e}")
        return None


    def ziggbee_devices(self, org, event, payload):
        if event=='devices':
            for p in payload:
                sensor_def = p.get('definition')
                if (sensor_def):
                    uuid = p.get('ieee_address')
                    sensor_name = slugify(sensor_def.get('model'))
                    try:
                        Device.objects.get(uuid__exact=uuid)
                        #logger.info(f'{org}: Device {uuid} exist, pass!')
                    except:
                        try:
                            Device.objects.create(
                                name=f'{sensor_name}: {uuid}',
                                uuid=uuid,
                                sensor=sensor_name,
                                description=sensor_def.get('description'),
                                vendor=sensor_def.get('vendor'),
                                model_id=sensor_def.get('model_id'),
                                org=org,
                                ip=sensor_def.get('network_address'),
                                datas=sensor_def.get('exposes'),
                                options=sensor_def.get('options'),
                            )
                            logger.info(f'Device registration {uuid} done')
                        except Exception as e:
                            raise Exception(f"Device creation error: {e}")
        elif event=='state':
            logger.info(f"state..........{org} {payload}\n")
        return None


    def registration(self, org, uuid):
        try:
            device = self.device_registry.get(uuid)
            if device is not None:
                return device
            #logger.info(f"{org}: device {device.sensor}: {uuid} is registered")
            self.device_registry[uuid] = Device.objects.get(uuid__exact=uuid)
            return self.device_registry[uuid]

        except Exception as e:
            logger.error(f"{org}::{uuid} device registration error: {e}")
            return None


    def is_device_registered(self, args, payload):
        try:           
            org = args.get('org')
            uuid = args.get('uuid')
            if org==self.org:
                if args.get('evt')=='report':
                    return self.devices_data(org, uuid, payload)
            elif org==self.gw:
                ## mqtt gateway
                if uuid =='bridge':
                    return self.ziggbee_devices(org, args.get('evt'), payload)
        except Exception as e:
            logger.info(f'It is not a device or a gateway: {e}')    
            return None
        return self.registration(org, uuid)
    
    
    def get_process_instance(self, args, payload):
        try:
            device = self.is_device_registered(args, payload)
            if device:
                if device.uuid in self.processus:
                    return self.processus[device.uuid]  
        except Exception as e:
            logger.error(f'get_process_instance: {e}')
        return None
    
        
    def _on_bytes_callback(self, topic, payload):
        try:
            args = Topic(topic)
            instance = self.get_process_instance(args, payload)
            if instance:
                instance.onBytesProcessing(args, payload)    
        except Exception as e:
            logger.error(f'_on_bytes_callback: {e}')    


    def _on_message_callback(self, topic, payload):
        try:
            args = Topic(topic)          
            instance = self.get_process_instance(args, payload)
            if instance:
                instance.onMessageProcessing(args, payload)    
        except Exception as e:
            logger.error(f'_on_message_callback: {e} {topic}')

