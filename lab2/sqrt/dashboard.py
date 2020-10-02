import time
import zmq
import pprint

def dashboard():
    context = zmq.Context()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://127.0.0.1:5558")
    #file = open("output.txt", "w+")
    while True:
        result = results_receiver.recv_json()
        pprint.pprint(result['consumer'])
        #file.write(str(result['consumer']) + "\n")

dashboard()