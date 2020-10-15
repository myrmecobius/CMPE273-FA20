import zmq
import random
import sys
import time

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://127.0.0.1:5556")


msg = socket.recv().decode()
print(msg)
socket.send("client message to server1".encode())
socket.send("client message to server2".encode())
time.sleep(1)