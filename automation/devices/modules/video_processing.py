'''
Created on 13 juil. 2024

@author: denis
'''
import logging, pathlib, threading, json
from django.conf import settings
from devices.modules.processing import Base
from devices.modules.video_replay import VideoReplay


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

            
class RecordBytes(Base):
    
    def init(self):
        self.counter = 0
        self.video_replay = None
        
    def state_toggle(self, state):
        return 'pause' if state=='play' else 'play'
                    
    def get_filename(self, args, media_root, fps=None, ext='wav'):
        uuid, counter, ts = args.get('uuid'), args.get('counter'), args.get('ts')
        lat, lon = args.get('lat'), args.get('lon')
        sdir = pathlib.Path(f"{media_root}/{uuid}")
        if not sdir.is_dir():
            sdir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Create a directory: mkdir {sdir}")
        if fps:
            return str(sdir / f"{ts}-{counter}-{lat}_{lon}-{fps}.{ext}")  
        return  str(sdir / f"{ts}-{counter}-{lat}_{lon}.{ext}")        
        
    def create_wavefile(self, args, payload):
        filename =  self.get_filename(args, settings.AUDIO_ROOT, ext='wav')
        with open(filename, 'wb') as f:
            f.write(payload)

    def create_jpgfile(self, args, payload):
        filename =  self.get_filename(args, settings.VIDEO_ROOT, ext='jpg', fps=args.get('fps'))
        with open(filename, 'wb') as f:
            f.write(payload)        

    def onMessageProcessing(self, args, payload):
        super().onMessageProcessing(args, payload)
        if args.get('evt')=='set':
            # from dashboard
            if args.get('action')=='save':
                self.device.record = int(payload.get('record'))
                self.device.options = json.dumps(payload)
                self.device.save()
                logger.info(f"Record={self.device.record} from dashbord, options={self.device.options}")
                
        #elif args.get('evt') == 'rec':
        #    # from device model signal
        #    if args.get('action') == 'save':
        #        self.device.record = int(payload.get('record'))
        #        logger.info(f"Record={self.device.record} from device model signal")
                             
        elif args.get('evt') == 'replay':
            state = payload.get('state')
            if args.get('action') == 'toggle':
                if self.video_replay is None:
                    self.video_replay = VideoReplay(self, self.device, **payload)
                    self.video_replay.start()
                    
                self.video_replay.state = self.state_toggle(state)
                self.mqtt_publish(f'{self.device.basetopic}/replay-state', action='toggle', state=self.video_replay.state, msg='pending') 
                
            elif args.get('action') == 'reset':
                if self.video_replay is not None:
                    self.video_replay.stop()
                    threading.Event().wait(2)  
                self.mqtt_publish(f'{self.device.basetopic}/replay-state', action='reset', state='pause', msg='ready')
                
            elif args.get('action') == 'fps':
                if self.video_replay is not None:
                    self.video_replay.fps = payload.get('fps')
                    self.mqtt_publish(f'{self.device.basetopic}/replay-state', action='fps', fps=self.video_replay.fps)
                    
    def onBytesProcessing(self, args, payload):
        if self.device.record > 0:
            counter = int(args.get('counter'))
            if self.counter < counter:
                self.counter = counter
                if  self.device.sensor == 'camera':
                    self.create_jpgfile(args, payload)
                elif self.device.sensor == 'audio':
                    self.create_wavefile(args, payload)

