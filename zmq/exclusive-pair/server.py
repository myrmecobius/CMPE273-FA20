import zmq
import random
import sys
import time

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://127.0.0.1:5556")

while True:
    socket.send("Server message to client3".encode())
    msg = socket.recv().decode()
    print(msg)
    time.sleep(1)