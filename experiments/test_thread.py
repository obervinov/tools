#!/usr/bin/env python3

import threading
import time


def test(index_thread):
    print("index: " + str(index_thread))
    print("thread count: " + str(threading.active_count()))
    print("current thread: " + str(threading.current_thread().getName()))
    time.sleep(3)


def return_results(a, b):
    a = a + 1
    b = b + 2
    return a


thread_poll = list()
thread_poll_size = 10
index_thread = 0


while index_thread < 100:
    a = 0
    b = 0
    if index_thread < thread_poll_size:
        thread_job = threading.Thread(target=return_results, args=(a, b, ))
        thread_poll.append(thread_job)
        thread_job.start()
        index_thread = index_thread + 1
    else:
        for index, thread in enumerate(thread_poll):
            ret = thread.join()
            print("return_results: " + str(ret))
        index_thread = 0
        print('clear threads')
        del thread_poll[:]
