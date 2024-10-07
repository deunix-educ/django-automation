'''
Created on 21 août 2024

@author: denis
'''
import logging
import asyncio
from abc import ABC
from pyrfc3339 import generate
from reduct import Client, Bucket, BucketSettings, QuotaType


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReductStoreBase(ABC):
    token = None
    url = None
    quota_type=QuotaType.FIFO
    quota_size=1000_000_000

    def __init__(self, name='sensor.name'):
        self.bucket_name = name
        self.client = Client(self.url, api_token=self.token)
        self.bucket: Bucket = asyncio.run(self.create_bucket())

    def date_to_RFC3339(self, dt):
        dte = generate(dt, accept_naive=True)
        return dte   
    
    async def create_bucket(self): 
        settings = BucketSettings(
            quota_type=self.quota_type,
            quota_size=self.quota_size,
        )            
        return await self.client.create_bucket(self.bucket_name, settings, exist_ok=True)
        
    async def change_bucket(self, **settings): 
        new_settings = BucketSettings(**settings)
        await self.bucket.set_settings(new_settings)         
    
    async def remove_bucket(self): 
        await self.bucket.remove()

    def write(self, entry_name, data, timestamp=None, content_type=None, labels=None):
        asyncio.run(self.bucket.write(entry_name, data, timestamp=timestamp, content_type=content_type, labels=labels))
        
    def query(self, entry_name, start, stop):   
        return self.bucket.query(entry_name, start=start, stop=stop)

    async def read(self, entry_name, timestamp, head=False):   
        record = self.bucket.read(entry_name, timestamp=timestamp, head=head)
        return await record.read_all()
    
    
    """
    def dataframe(self, measurement, dataname, start='-1m', agg_fn='mean', frequency='10s', empty=True, desc=True):
        begin = f'|> range(start: {start})'
        measure = f'|> filter(fn: (r) => r["_measurement"] == "{measurement}")'
        name = f'|> filter(fn: (r) => r["_field"] == "{dataname}")'
        aggregate = f'|> aggregateWindow(column: "_value", every: {frequency}, fn: {agg_fn}, createEmpty: {"true" if empty else "false"})'
        pivot = f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
        drop = f'|> drop(columns: ["_start", "_stop"])'
        query = f'from(bucket: "{self.bucket}") {begin} {measure} {name} {aggregate} {pivot} {drop}'

        df =  self.query_api.query_data_frame(query, org=self.org)
        df = df.drop(['table'], axis=1)
        df.set_index("_time", inplace = True)       
        return df
    """
