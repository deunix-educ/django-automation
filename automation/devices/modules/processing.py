'''
Created on 13 juil. 2024

@author: denis
'''
import logging, json
from django.conf import settings
from devices.modules.influxdb import InfluxdbBase
from devices.modules.reductstore import ReductStoreBase
from contrib import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Influxdb(InfluxdbBase):
    token = settings.INFLUXDB_TOKEN
    org_id = settings.INFLUXDB_ORG_ID
    org = settings.INFLUXDB_ORG
    url = settings.INFLUXDB_URL

    def __init__(self, bucket='sensor.name'):
        super().__init__(bucket)

    def write(self, device, datas):
        taglist = json.loads(device.tags) if device.tags else {}
        tags = dict(
            location=device.location.name,
            **taglist
        )
        super().write(measurement=device.sensor, tags=tags, datas=datas)


class ReductStore(ReductStoreBase):
    token = settings.REDUCTSTORE_TOKEN
    url = settings.REDUCTSTORE_URL

    def __init__(self, bucket_name='sensor.name'):
        super().__init__(bucket_name)
        

class Base(object):

    def __init__(self, parent, device, links):
        self.parent = parent
        self.device = device
        self.links = links
        self.org = parent.org
        self.gateway = parent.gw
        self.device_registry = parent.device_registry
        self.init()
            
    def init(self):
        pass
 
    def onBytesProcessing(self, args, payload):
        pass
       
    def onMessageProcessing(self, args, payload):
        if args.get('evt')=='rec' and args.get('action')=='save':  # from device model signal
            self.device.record = int(payload.get('record'))
            logger.info(f"Record={self.device.record} from device model signal")
    
    def _data(self, items, payload):
        d = {}
        for item in items:
            d[item] = payload.get(item)
        return d

    def mqtt_publish(self, topic, **payload):
        self.parent._publish_message(topic, **payload)
        logger.info(f"Device publish {topic}: {payload}")
        
    def mqtt_publish_bytes(self, topic, frame):
        if frame:
            #logger.info(f"Device publish frame: {topic}")
            self.parent._publish_bytes(topic, frame)
        

class Record(Base):
    
    def init(self):
        self.client_db = Influxdb(bucket=self.device.sensor)
             
    def onMessageProcessing(self, args, payload):
        super().onMessageProcessing(args, payload)
        if self.device.record > 0:
            datas = self._data(self.device.get_items, payload)  # @UnusedVariable
            self.client_db.write(self.device, datas)
    

class PushButton(Base):
    _buttons = [False, ]
    _state   = ['OFF', 'ON', 'TOGGLE']
    
    V_OFF, V_ON, V_TOGGLE = 0, 1, 2
    
    def init(self):
        self.relay = self.links[0]
        self.timeout = 0.1
    
    def get_state(self, btn=0):
        return self._buttons[btn]
    
    def set_state(self, btn=0, state=False):
        self._buttons[btn] = state
            
    def state_value(self, btn=0):
        return self._state[self.V_ON] if self.get_state(btn) else self._state[self.V_OFF]

    def toggle(self, btn=0):
        state = not self.get_state(btn)
        self.set_state(btn, state)
        return state

    def action(self, state_value):
        self.mqtt_publish(f'{self.relay.link.org}/{self.relay.link.uuid}/set', state=state_value)
        #print(f'{self.relay.link.org}/{self.relay.link.uuid}/set', state_value)
        utils.wait_for(self.timeout)
        
    def button_action(self, btn=0, state_value=None):
        if state_value in [self._state]:
            if state_value==self._state[self.V_TOGGLE]:
                self.toggle(btn)
            else:
                self.set_state(btn=0, value=True)
            self.action(self.state_value(btn))           
        
    def onMessageProcessing(self, args, payload):
        if args.get('evt') == 'set':
            self.button_action(btn=0, state_value=payload.get('state'))
            
            
class RelaySwitch(PushButton):
    _state = ['CLOSE', 'OPEN', 'TOGGLE', ]
        
 
class RollerShutterRelaySwitch(PushButton):
    _buttons = [False, False, ]
    _state = ['CLOSE', 'OPEN', 'STOP', ]
    _switch = {'single_left': 0, 'single_right': 1}
    V_CLOSE, V_OPEN, V_STOP = 0, 1, 2

    def action_stop(self, btn):
        self.action(self._state[self.V_STOP])
        self.set_state(btn, state=False)

    def action_close(self):
        self.action_stop(btn=1)
        state = self.toggle(btn=0)
        if state:
            self.action(self._state[self.V_CLOSE])
    
    def action_open(self):
        self.action_stop(btn=0)
        state = self.toggle(btn=1)
        if state:
            self.action(self._state[self.V_OPEN])
           
    def onMessageProcessing(self, args, payload):
        action = payload.get('action')
        if action==self._state[self.V_OPEN]:
            self.action_open()        
        elif action==self._state[self.V_CLOSE]:
            self.action_close()
        elif action==self._state[self.V_STOP]:
            self.action_stop()


class VirtualDoubleSwitch(RollerShutterRelaySwitch):
    open = False
    
    def button_state(self, btn=0):
        return 'on' if  self.get_state(btn) else 'off'
    
    def button_states(self):
        uuid = f'{self.device.uuid}'
        return {f'{uuid}-0': self.button_state(btn=0), f'{uuid}-1': self.button_state(btn=1)}
        
    def action_close(self):
        super().action_close()
        self.mqtt_publish(f'{self.org}/{self.device.uuid}/state', states=self.button_states())

    def action_open(self):
        super().action_open()
        self.mqtt_publish(f'{self.org}/{self.device.uuid}/state', states=self.button_states())
         
    def action_toggle(self):
        if not self.open:
            self.action_open()
        else: 
            self.action_close()
        self.open = not self.open
 
    def onMessageProcessing(self, args, payload):
        if args.get('evt')=='set':
            state = payload.get('state')
            if state=='TOGGLE':
                self.action_toggle()
            elif state==self._state[self.V_CLOSE]:
                self.action_close()
            elif state==self._state[self.V_OPEN]:
                self.action_open()               
