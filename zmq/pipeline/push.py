import zmq
import random

def worker():
    context = zmq.Context()
    # send work
    worker_sender = context.socket(zmq.PUSH)
    worker_sender.connect("tcp://127.0.0.1:5558")
    
    for data in range(10):
        result = { 'num' : data }
        worker_sender.send_json(result)
        print("sent with {}".format(data))

worker()