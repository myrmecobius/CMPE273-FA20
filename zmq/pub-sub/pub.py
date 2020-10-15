import zmq
import random
import time

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5556")

while True:
    topic = random.randrange(9999,10005)
    messagedata = random.randrange(1,215) - 80
    print("%d %d" % (topic, messagedata))
    socket.send(f"{topic} {messagedata}".encode())
    time.sleep(1)