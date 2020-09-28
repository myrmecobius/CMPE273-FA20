import time
import zmq

def generator():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://127.0.0.1:5557")
    for num in range(10001):
        print("num is {}".format(num))
        work_message = { 'num' : num }
        zmq_socket.send_json(work_message)

generator()