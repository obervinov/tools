#!/usr/bin/env python3

import datetime
import random
import string
import time
import sys
import urllib.parse
from pymongo import MongoClient

ACTION = sys.argv[1]
HOST = "mongodb-host-1"
PORT = "27017"
USER = urllib.parse.quote_plus('python')
PASS = password = urllib.parse.quote_plus('python')
LIMIT = 2000
RPS = 5000
SLEEP = 1


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


if ACTION == "read":
    DB = 'dbname'
    COLLECTION = 'collection'

    client = MongoClient('mongodb://%s:%s@%s:%s/admin' % (USER, PASS, HOST, PORT))
    db = client[DB]
    collection = db[COLLECTION]

    print("### RPS: "+str(RPS)+" LIMIT: "+str(LIMIT)+" SLEEP: "+str(SLEEP)+" ###")
    print(client)
    print(collection)
    print("===> START TEST FIND REQUESTS:")
    while True:
        for i in range(0, RPS):
            cursor = collection.find({}).limit(LIMIT)
            print("Find request #"+str(i))
        client.close()
        CURRENT_TIME = datetime.datetime.today()
        print("### "+str(CURRENT_TIME))
        time.sleep(SLEEP)

elif ACTION == "write":
    DB = 'dbname'
    COLLECTION = 'colelction'

    client = MongoClient('mongodb://%s:%s@%s:%s/admin' % (USER, PASS, HOST, PORT))
    db = client[DB]
    collection = db[COLLECTION]

    print("### RPS: "+str(RPS)+" LIMIT: "+str(LIMIT)+" SLEEP: "+str(SLEEP)+" ###")
    print()
    print(client)
    print(collection)
    print()
    print("===> START TEST WRITE REQUEST DOCS:")
    while True:
        for i in range(0, RPS):
            post = {"author": "obervinov",
                    "text": "This is pymongo testing write docs",
                    "tags": ["mongodb", "python", "pymongo"],
                    "date": datetime.datetime.utcnow(),
                    "uid": get_random_string(24)}

            test = db.test
            post_id = test.insert_one(post).inserted_id
            print(post_id)
            CURRENT_TIME = datetime.datetime.today()
            print("### "+str(CURRENT_TIME))
        client.close()
        time.sleep(SLEEP)

else:
    print("Exit")
    exit()
