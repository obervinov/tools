from asyncore import read
import threading
import time
import queue

def read_q(q):
    for job in iter(q.get, None):
        print(job)
        time.sleep(30)

q = queue.Queue()
q.put("1")
q.put("2")
q.put("3")
q.put("4")
q.put("5")

thread = threading.Thread(target=read_q, args=(q, ))
thread.start()

q.put("10")
q.put("20")
q.put("30")
q.put("40")
q.put("50")
print(thread.is_alive())
thread.join()