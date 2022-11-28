#!/usr/bin/env python3

import os
import logging
import time
import threading
from boto3.session import Session

logging.basicConfig(level=logging.DEBUG)


def s3_get_files_list_multythreds():
    thread_poll = list()
    thread_poll_size = 500
    index_thread = 0
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

    for obj in bucket.objects.filter(Prefix='dir1/'):
        if index_thread < thread_poll_size:
            thread_job = threading.Thread(target=s3_dowload_files, args=(obj.key, BUCKET, s3, ))
            thread_poll.append(thread_job)
            thread_job.start()
            index_thread = index_thread + 1
            print("##### > THREAD COUNT: " + str(threading.active_count()))
        else:
            for index, thread in enumerate(thread_poll):
                thread.join()
            index_thread = 0
            del thread_poll[:]


def s3_dowload_files(obj, BUCKET, s3):
    print('{0}'.format(obj))
    DST_FILENAME = "/opt/s3/bucket/" + obj
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
            s3.meta.client.download_file(BUCKET, obj, DST_FILENAME)
        except Exception:
            print(f"download_file failed {obj}")
            print("sleep timeout 3s")
            time.sleep(3)
            try:
                print(f"retry download_file {obj}")
                s3.meta.client.download_file(BUCKET, obj, DST_FILENAME)
            except Exception:
                print(f"download_file ERROR {obj}")
                print("next file... ")
                pass


s3_get_files_list_multythreds()
