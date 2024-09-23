'''
Created on 28 juil. 2024

@author: denis
'''
import time, logging
import threading
#from datetime import datetime
from io import BytesIO
from PIL import Image
from django.conf import settings
from contrib import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Replay(threading.Thread):
    
    def __init__(self, parent):
        super().__init__(daemon=True)
        self.stop_replay = threading.Event()
        self.parent = parent
        self.begin_t = 0  
        self._fps = 0
        self._state = 'pause'
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, v):
        self._state = v

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, v):
        self._fps = v
                   
    def millis(self):
        return round(time.time() * 1000)

    def wait_for_frame(self, begin_t, fps):
        duration = float( (self.millis() - begin_t)/1000)
        sleep = 1/fps - duration
        if sleep > 0:
            threading.Event().wait(sleep)


class VideoReplay(Replay):

    def __init__(self, parent, device, **params):      
        super().__init__(parent)
        self.device = device
        self.video_root = settings.VIDEO_ROOT / f"{device.uuid}"
        self.fps = params.get('fps')
        self.lat_n = params.get('lat_n')
        self.lat_s = params.get('lat_s')
        self.lon_w = params.get('lon_w')
        self.lon_e = params.get('lon_e')
        self.state = 'play'
        self.begin, self.end, self.mask = self.dates_filter(params.get('start_date'), params.get('end_date'))       
        self.geo = True if self.lat_n and self.lat_s and self.lon_w and self.lon_e else False
    
    def dates_filter(self, begin, end):
        mask = ""
        if begin:
            begin = int(begin)
            end = int(end) if end else utils.ts_now(m=1000)
            mask = len(str(end-begin))
            if mask > 0:
                mask = str(begin)[:-mask]
            else:
                begin = end = mask = ""
        else:
            begin = ""
            if end:
                end = int(end)
        return begin, end, mask
        
    def params(self, filename):
        ts, counter, lat_lon, fps = filename.split('-')
        lat, lon = lat_lon.split('_')       
        return int(ts), int(counter), lat, lon, int(fps)
    
    def in_geo_array(self, lat, lon):
        lat, lon = utils.conv_gps(lat), utils.conv_gps(lon)
        if  lat and lon:
            return (self.lat_n <= lat <= self.lat_s) and (self.lon_w <= lon <= self.lon_e)
        return False

    def stop(self):
        self.stop_replay.set()
        
    def run(self):
        # date begin filter
        pattern = f'{self.mask}*.jpg'             
        d = iter(sorted(self.video_root.glob(pattern)))
        while not self.stop_replay.is_set():
            try:
                if self.state == 'play':
                    begin_t = self.millis()
                    f = next(d)
                    ts, counter, lat, lon, fps = self.params(f.stem)
                    
                    #print(self.begin, int(ts), int(ts) < self.begin)
                    # fps filter
                    if self.fps:
                        fps = int(self.fps)
                        
                    # date begin filter
                    if self.begin and int(ts) < self.begin:
                        continue
                    # date end filter
                    if self.end and int(ts) > self.end:
                        break
                    # geo filter
                    if self.geo and not self.in_geo_array(lat, lon):
                        continue
                    
                    with BytesIO() as output:
                        with Image.open(f) as img:
                            img.save(output, 'JPEG')
                        payload = output.getvalue()
                        
                        topic = f'{self.device.basetopic}/mjpg/{ts}/{counter}/{lat}/{lon}/{fps}'
                        self.parent.mqtt_publish_bytes(topic, payload)
                        
                    self.wait_for_frame(begin_t, fps)
                else:
                    threading.Event().wait(1) 

            except StopIteration:
                break
        self.parent.video_replay = None
        self.parent.mqtt_publish(f'{self.device.basetopic}/replay-state', action='end', state='pause', msg='finished')
        
        