import zmq
import requests

# ZeroMQ Context
context = zmq.Context()

# Define the socket using the "Context"
sock = context.socket(zmq.REP)
sock.bind("tcp://127.0.0.1:1234")

# Run a simple "Echo" server
while True:
    message = sock.recv()
    message = message.decode()
    reply_msg = "Request: " + message
    response = requests.get(message)
    reply_msg += f" got status code {response.status_code}"
    sock.send(reply_msg.encode())
    print(reply_msg)