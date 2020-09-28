import zmq
import random

def consumer():
    # consumer_id = random.randrange(1,10005)
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:5557")
    # send work
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect("tcp://127.0.0.1:5558")
    
    while True:
        work = consumer_receiver.recv_json()
        data = work['num']
        sqrdata = int(data)
        sqrdata = sqrdata **(0.5)
        result = { 'consumer' : sqrdata, 'num' : data}
        # if data%2 == 0: 
        consumer_sender.send_json(result)
        print("sent with {}".format(data))

consumer()