import zmq
import time
import sys
from itertools import cycle

numItems = 10 # Number of data points to send

def create_clients(servers):
    producers = {}
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.PUSH)
        producer_conn.bind(server)
        producers[server] = producer_conn
    return producers
    
def toInt( someString ): #convert string to int by concatenating int of each char
    result = ""
    for c in someString:
        result += str(ord(c))
    return int(result)

def consistentHash( keyStr ): # Hashing for consistent hashing
    num = toInt( keyStr )
    x = num % 3600
    a = 2837
    b = 1984
    return (a*x + b) % 3600

def weight( keyStr, servStr ): # Hashing for HRW hashing
    keyInt = toInt( keyStr ) % 3600
    servInt = toInt ( servStr ) % 3600
    a = 1492
    b = 2207
    result = (a * pow( (a * servInt + b), keyInt, 3600) + b) % 3600
    return result

def chooseServerConsistent( keyStr, binHash ): # choose server for consistent hashing
    keyHash = consistentHash( keyStr )
    servs = [x for x in binHash.keys()]
    servs.sort()
    #print(f"servs = {servs}")
    for x in servs:
        if x >= keyHash:
            #print(f"Hashing {keyHash} to {x} on bin {binHash[x]}")
            return binHash[x]
    #print(f"Hashing {keyHash} to {servs[0]} on bin {binHash[servs[0]]}")
    return binHash[servs[0]]

def chooseServerHRW( keyStr, serverList ): #choose server for HRW hashing
    serverHash = dict()
    weights = []
    for s in serverList:
        w = weight( keyStr, s )
        serverHash[w] = s
        weights.append(w)
    #print(f"weights are {serverHash}, choosing {max(weights)} corresponding to {serverHash[max(weights)]}")
    return serverHash[max(weights)]

def generate_data_round_robin(servers, producers):
    print("Starting Round Robin...")
    pool = cycle(producers.keys())
    counts = dict()
    for num in range(numItems):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        k = next(pool)
        #print(f"Sending data:{data} to bin {k}")
        #print()
        producers[k].send_json(data)
        countsKey = k.split(":")[-1]
        if not counts.get(countsKey):
            counts[countsKey] = 1
        else:
            counts[countsKey] += 1
        time.sleep(1)
    print(f"Done. Number of items sent to bin: {counts}")
    print()

def generate_data_consistent_hashing(servers, producers):
    print("Starting Consistent Hashing...")
    binHash = dict()
    for s in servers:
        binHash[consistentHash(s)] = s
    counts = dict()
    for num in range(numItems):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        sendBin = chooseServerConsistent( data["key"], binHash )
        #print(f"Sending data:{data} to bin {sendBin}")
        #print()
        producers[sendBin].send_json(data)
        countsKey = sendBin.split(":")[-1]
        if not counts.get(countsKey):
            counts[countsKey] = 1
        else:
            counts[countsKey] += 1
        time.sleep(1)
    print(f"Done. Number of items sent to bin: {counts}")
    print()
    
def generate_data_hrw_hashing(servers, producers):
    print("Starting...")
    counts = dict()
    for num in range(numItems):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        sendBin = chooseServerHRW( data["key"], servers )
        #print(f"Sending data:{data} to bin {sendBin}")
        #print()
        producers[sendBin].send_json(data)
        countsKey = sendBin.split(":")[-1]
        if not counts.get(countsKey):
            counts[countsKey] = 1
        else:
            counts[countsKey] += 1
        time.sleep(1)
    print(f"Done. Number of items sent to bin: {counts}")
    print()
    
if __name__ == "__main__":
    servers = []
    num_server = 1
    if len(sys.argv) > 1:
        num_server = int(sys.argv[1])
        print(f"num_server={num_server}")
        
    for each_server in range(num_server):
        server_port = "200{}".format(each_server)
        servers.append(f'tcp://127.0.0.1:{server_port}')
    
    producers = create_clients(servers)
    print()

    print("Servers:", servers)
    print()
    generate_data_round_robin(servers, producers)
    generate_data_consistent_hashing(servers, producers)
    generate_data_hrw_hashing(servers, producers)
    
