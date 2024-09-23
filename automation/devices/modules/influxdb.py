'''
Created on 21 août 2024

@author: denis
'''
import logging
from abc import ABC
from datetime import datetime

from pyrfc3339 import generate
from influxdb_client import InfluxDBClient, BucketRetentionRules, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfluxdbBase(ABC):
    token = None
    org_id = None
    org = None
    url = None

    def __init__(self, bucket='sensor.name'):
        self.bucket = bucket
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS, error_callback=self.error_cb, success_callback=self.success_cb)
        self.buckets_api = self.client.buckets_api()      
        self.delete_api = self.client.delete_api()
        self.query_api = self.client.query_api()
        self.create_bucket()
        
    def date_to_RFC3339(self, dt):
        dte = generate(dt, accept_naive=True)
        return dte

    def success_cb(self, arg, data):
        logger.error(f"{arg}\n{data}")


    def error_cb(self, arg, data, error):
        logger.error(f"{arg}: {error}\n{data}")
    
    
    def create_bucket(self, retention_days=30):
        retention_seconds = retention_days * 86400
        try:
            if not self.buckets_api.find_bucket_by_name(self.bucket):
                retention_rules = BucketRetentionRules(type="expire", every_seconds=retention_seconds)
                self.buckets_api.create_bucket(bucket_name=self.bucket, org=self.org, retention_rules=retention_rules)
        except Exception as e:
            print(f"create_bucket error: {e}")
            
            
    def delete(self, measurement, date_start=None, date_stop=None):
        start = datetime(1970, 1, 1) if date_start is None else date_start
        stop = datetime.now() if date_stop is None else date_stop
        start, stop = self.date_to_RFC3339(start),  self.date_to_RFC3339(stop)
        self.delete_api.delete(start, stop, f'_measurement="{measurement}"', bucket=self.bucket, org=self.org)
        
      
    def write(self, measurement, tags={}, datas={}):
        #print(f"Base::{device.name}........: format: {datas}")
        ts = datas.pop('time', 1)
        dict_structure = {
            "measurement": measurement,
            "tags": tags,
            "fields": datas,
            "time": ts
        }
        point = Point.from_dict(dict_structure, WritePrecision.S)        
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        self.write_api.close()


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
    
