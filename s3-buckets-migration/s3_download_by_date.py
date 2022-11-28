#!/usr/bin/env python3

import os
import time
import datetime
import multiprocessing as mp
import logging
from boto3.session import Session

logging.basicConfig(level=logging.DEBUG)


def s3_dowload_files():
    ACCESS_KEY = '***'
    SECRET_KEY = '***'
    ENDPOINT = 'https://s3.example.com'
    BUCKET = "bucket"

    session = Session(
                  aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY
              )
    s3 = session.resource('s3', endpoint_url=ENDPOINT)
    bucket = s3.Bucket(BUCKET)

    for obj in bucket.objects.filter(Prefix='prod/'):
        if obj.last_modified.replace(tzinfo=None) > datetime.datetime(2021, 4, 5, tzinfo=None):
            print('{0} {1}'.format(obj.last_modified, obj.key))
            jobs.append(pool.apply_async(download_file(obj, BUCKET, s3)))


def download_file(obj, BUCKET, s3):
    DST_FILENAME = "/opt/s3/bucket" + obj.key
    PATH_ARRAY = DST_FILENAME.split("/")
    PATH_LEN = len(PATH_ARRAY)
    DIR_PATH = ""
    if PATH_LEN > 0:
        del PATH_ARRAY[-1]
    i = 0
    for path in PATH_ARRAY:
        if i == 0:
            DIR_PATH = path
            i = i + 1
        else:
            DIR_PATH = DIR_PATH + "/" + path
    print(DIR_PATH)
    os.makedirs(DIR_PATH, exist_ok=True)
    if os.path.isfile(DST_FILENAME):
        print(f"{DST_FILENAME} file exist")
    else:
        try:
            s3.meta.client.download_file(BUCKET, obj.key, DST_FILENAME)
        except Exception:
            print("download_file failed "+obj.key)
            print("sleep timeout 3s")
            time.sleep(3)
            try:
                print("retry download_file "+obj.key)
                s3.meta.client.download_file(BUCKET, obj.key, DST_FILENAME)
            except Exception:
                print("download_file ERROR "+obj.key)
                print("next file... ")
                pass


pool = mp.Pool(100)
jobs = []

s3_dowload_files()

for job in jobs:
    job.get()

pool.close()
