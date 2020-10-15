import zmq

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect ("tcp://127.0.0.1:5556")

# Subscribe to zipcode, default is NYC, 10001
shouldFilter = False
if shouldFilter:
    topicfilter = "10001"
    socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
else:
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

#total_value = 0
#for update_nbr in range (5):
while True:
    string = socket.recv().decode()
    topic, messagedata = string.split()
    #total_value += int(messagedata)
    print(topic, messagedata)

#print("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))