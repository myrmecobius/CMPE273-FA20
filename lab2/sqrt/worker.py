import zmq
import random

def worker():
    context = zmq.Context()
    # recieve work
    worker_receiver = context.socket(zmq.PULL)
    worker_receiver.connect("tcp://127.0.0.1:5557")
    # send work
    worker_sender = context.socket(zmq.PUSH)
    worker_sender.connect("tcp://127.0.0.1:5558")
    
    while True:
        work = worker_receiver.recv_json()
        data = work['num']
        sqrdata = int(data)
        sqrdata = sqrdata **(0.5)
        result = { 'consumer' : sqrdata, 'num' : data}
        worker_sender.send_json(result)
        print("sent with {}".format(data))

worker()