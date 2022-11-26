import logging
import os
from boto3.session import Session
from botocore.exceptions import ClientError
from botocore.config import Config

logging.basicConfig(level=logging.DEBUG)



def s3_src_bucket_list():
    ACCESS_KEY_SRC='***'
    SECRET_KEY_SRC='***'
    ENDPOINT_SRC = "https://s3.example.com"
    Session(aws_access_key_id=ACCESS_KEY_SRC,
            aws_secret_access_key=SECRET_KEY_SRC
            )
    
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_SRC,aws_access_key_id=ACCESS_KEY_SRC,aws_secret_access_key=SECRET_KEY_SRC)
    
    response = s3.list_buckets()

    print('Buckets list:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')



def read_local_files():
    local_path = '/tmp/migration/'
    files = []
    for r, d, f in os.walk(local_path):
        for file in f:
            files.append(os.path.join(r, file))
    for f in files:
        object_name = f.replace("/tmp/migration/", "")
        ext_file = object_name.split(".")
        content_type = "image/" + ext_file[1]
        s3_dst_upload_files(f,object_name,content_type)




def s3_dst_upload_files(file_name, object_name=None, content_type=None):
    if object_name is None:
        object_name = file_name
    if content_type is None:
        content_type = 'image/boto3-python'
    
    ACCESS_KEY_DST = '**'
    SECRET_KEY_DST = '**'
    ENDPOINT_DST = 'https://s3.example.com'
    BUCKET_DST = "bucket"
    s3_dst_config = Config(
        region_name = 'us-east-1',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    s3_dst_client = boto3.client('s3', endpoint_url=ENDPOINT_DST,aws_access_key_id=ACCESS_KEY_DST,aws_secret_access_key=SECRET_KEY_DST,config=s3_dst_config)

    try:
        s3_dst_client.upload_file(file_name, BUCKET_DST, object_name, ExtraArgs={'ContentType': content_type})
    except ClientError as e:
        logging.error(e)
        return False
    return True    



def s3_src_dowload_files():
    ACCESS_KEY_SRC = '***'
    SECRET_KEY_SRC = '***'
    ENDPOINT_SRC = 'https://s3.example2.com'
    BUCKET_SRC = "bucket"

    session = Session(aws_access_key_id=ACCESS_KEY_SRC,
                    aws_secret_access_key=SECRET_KEY_SRC)
    s3 = session.resource('s3', endpoint_url=ENDPOINT_SRC)
    bucket = s3.Bucket(BUCKET_SRC)

    for bucket_object in bucket.objects.all():
        print(bucket_object)
        DST_FILENAME = "/tmp/migration/" + bucket_object.key
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

        s3.meta.client.download_file(BUCKET_SRC,bucket_object.key, DST_FILENAME)
    
    read_local_files()



s3_src_bucket_list()
s3_src_dowload_files()