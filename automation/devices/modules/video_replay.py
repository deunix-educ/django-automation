'''
Created on 28 juil. 2024

@author: denis
'''
import time, logging
import threading
import asyncio
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.conf import settings
from contrib import utils
from devices.modules.processing import ReductStore
from reduct.time import TIME_PRECISION


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Replay():
    
    def __init__(self, parent, **params):
        self.parent = parent
        self.begin_t = 0  
        self._fps = 0
        self._state = 'pause'
        
        self.state = 'play'        
        self.fps = params.get('fps', 0)
        self.lat_n = params.get('lat_n')
        self.lat_s = params.get('lat_s')
        self.lon_w = params.get('lon_w')
        self.lon_e = params.get('lon_e')
        self.geo = True if self.lat_n and self.lat_s and self.lon_w and self.lon_e else False
        
        self.begin, self.end = self.dates_filter(params.get('start_date'), params.get('end_date'), params.get('micros', 1))
 
    def dates_filter(self, begin, end, micros):
        # ms to us
        
        print("dates_filter",  begin, end, micros)
        
        if begin:
            begin = int(begin)
            end = int(end) if end else utils.ts_now(m=1000)
            if begin < end:
                return begin * micros, end * micros
        else:
            if end:
                return None, int(end) * micros
        return None, None    

    def in_geo_array(self, lat, lon):
        lat, lon = utils.conv_gps(lat), utils.conv_gps(lon)
        if lat and lon:
            return (self.lat_n <= lat <= self.lat_s) and (self.lon_w <= lon <= self.lon_e)
        return False
            
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

    def sleep_seconds(self, begin_t, fps):
        duration = float( (self.millis() - begin_t)/1000)
        if fps > 0:
            return 1/fps - duration
        return duration
          
    def wait_for_frame(self, begin_t, fps):
        sleep = self.sleep_seconds(begin_t, fps)
        if sleep > 0:
            threading.Event().wait(sleep)
            
    async def async_wait_for_frame(self, begin_t, fps):
        sleep = self.sleep_seconds(begin_t, fps)
        if sleep > 0:
            await asyncio.sleep(sleep)
    
    def start_replay(self):
        pass
    
    def stop_replay(self):
        pass


class VideoReplay(Replay):

    def __init__(self, parent, device, **params):      
        super().__init__(parent, micros=1, **params)
        self.device = device
        self.stop_replay = threading.Event()
        self.video_root = settings.VIDEO_ROOT / f"{device.uuid}"
        
    def params(self, filename):
        ts, counter, lat_lon, fps = filename.split('-')
        lat, lon = lat_lon.split('_')       
        return int(ts), int(counter), lat, lon, int(fps)
    
    def start_replay(self):
        worker = threading.Thread(target=self.worker, daemon=True)
        worker.start()
        
    def stop_replay(self):
        self.stop_replay.set()
    
    def get_mask(self):
        try:
            mask = len(str(self.end - self.begin))
            if mask > 0:
                return str(self.begin)[:-mask]            
        except:
            pass
        return ""
    
    def worker(self):
        ## mask
        mask = self.get_mask()
        # date begin filter
        pattern = f'{mask}*.jpg'             
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

            except Exception:
                # StopIteration
                break
        self.parent.video_replay = None
        self.parent.mqtt_publish(f'{self.device.basetopic}/replay-state', action='end', state='pause', msg='finished')


class BlobVideoReplay(Replay):
    
    def __init__(self, parent, device, **params):      
        super().__init__(parent, micros=1000, **params)
        self.device = device       
        self.client_db = ReductStore(bucket_name=self.device.sensor)

    def stop_replay(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.parent.video_replay = None
        self.parent.mqtt_publish(f'{self.device.basetopic}/replay-state', action='end', state='pause', msg='finished')
        
        print("BlobVideoReplay stop_replay.................")
        
    def start_replay(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever).start()
        asyncio.run_coroutine_threadsafe(
            self.records_read(self.device.uuid, self.begin, self.end), 
            self.loop
        )
        print("BlobVideoReplay start_replay.............")  

    async def records_read(self, entry_name, start, end):
        logger.info(f"BlobVideoReplay start replay {entry_name}::{datetime.fromtimestamp(start/TIME_PRECISION)}:{datetime.fromtimestamp(end/TIME_PRECISION)}")
        
        query = self.client_db.query(entry_name, start, end)
        while True:
            try:        
                if self.state == 'play':
                    begin_t = self.millis()
                    record = await anext(query)
                    content = await record.read_all()
                    # geo filter
                    lat, lon = record.labels.get('lat'), record.labels.get('lon')
                    if self.geo and not self.in_geo_array(lat, lon):
                        continue 
                    # fps filter
                    fps = int(self.fps) if self.fps else int(record.labels.get('fps', 0))
                    counter = int(record.labels.get('counter'))
                    ts = int(record.timestamp/1000)
                    topic = f'{self.device.basetopic}/mjpg/{ts}/{counter}/{lat}/{lon}/{fps}'
                    self.parent.mqtt_publish_bytes(topic, content)                    
                    await self.async_wait_for_frame(begin_t, fps)
                else:
                    await asyncio.sleep(1)
            except Exception:
                # StopAsyncIteration
                break        
        self.stop_replay()
    