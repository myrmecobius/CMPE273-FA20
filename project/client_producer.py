import zmq
import time
import sys
import os
import consul
from consistent_hashing import *
from hrw_hashing import *
from itertools import cycle

numItems = 20 # Number of data points to send
sleep_time = 0.5
terminate_services = False # terminate services after using

def create_clients(servers):
    producers = {}
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.REQ)
        producer_conn.bind(server)
        producers[server] = producer_conn
        time.sleep(1)
    return producers

def clearNodes():
    for s in servers:
        delete_cmd = {'op': "DELETE_ALL", "key":"", "value":""}
        producers[s].send_json(delete_cmd)
        result = producers[s].recv_json()
        if not result["result"]:
            print("Bad response")
            raise "BadResponseException"

def generate_data_round_robin(servers, producers, st):
    print("Starting Round Robin...")
    pool = cycle(producers.keys())
    counts = dict()
    for num in range(numItems):
        data = { 'op': "PUT" ,'key': f'key-{num}', 'value': f'value-{num}' }
        k = next(pool)
        #print(f"Sending data:{data} to bin {k}")
        #print()
        producers[k].send_json(data)
        result = producers[k].recv_json()
        if not result["result"]:
            print("Bad response")
            raise "BadResponseException"
        countsKey = k.split(":")[-1]
        if not counts.get(countsKey):
            counts[countsKey] = 1
        else:
            counts[countsKey] += 1
        time.sleep(st)
    print(f"Done. Number of items sent to bin: {counts}")
    print()

def inspect_nodes( serv ):
    node_counts = dict()
    for s in serv:
        data = { 'op':"GET_ALL", 'key':'', 'value': '' }
        producers[s].send_json(data)
        result = producers[s].recv_json()
        if not result["result"]:
            print("Bad response")
            raise "BadResponseException"
        result = result["collection"]
        node_counts[s.split(":")[-1]] = len(result)
    print(node_counts)
    print()

def add_node( cons, port, producers, servers ):
    # Get new node number
    print("Adding a new node on port " + port)
    new_server_key = f'tcp://127.0.0.1:{port}'
    new_server_hash = consistentHash(new_server_key)
    # Get binHash
    binHash = dict()
    for s in servers:
        binHash[consistentHash(s)] = s
    # Determine which node to split
    rehash_bin = chooseServerConsistent( new_server_key, binHash )
    #print(f"Rehashing node {rehash_bin}")
    servers.append(new_server_key)
    binHash[new_server_hash] = new_server_key
    # GET ALL from node to split
    data = { 'op':"GET_ALL", 'key':'', 'value': '' }
    producers[rehash_bin].send_json(data)
    result = producers[rehash_bin].recv_json()
    if not result["result"]:
        print("Bad response")
        raise "BadResponseException"
    result = result["collection"]
    # Add new node
    #print("Notifying Consul of new node on port " + str(port))
    cons.agent.service.register(name=port, port = int(port))
    time.sleep(1)
    # log change in producers
    context = zmq.Context()
    producer_conn = context.socket(zmq.REQ)
    producer_conn.bind(new_server_key)
    producers[new_server_key] = producer_conn
    # Rehash data
    print("Rehashing...")
    moved = 0
    for d in result:
        k = d["key"]
        v = d["value"]
        sendBin = chooseServerConsistent( k, binHash )
        if sendBin == new_server_key:
            # put into new server
            data = { 'op':"PUT", 'key': k, 'value': v }
            producers[new_server_key].send_json(data)
            result = producers[new_server_key].recv_json()
            if not result["result"]:
                print("Bad response")
                raise "BadResponseException"
            # delete from old server
            data = { 'op':"DELETE", 'key': k, 'value': v }
            producers[rehash_bin].send_json(data)
            result = producers[rehash_bin].recv_json()
            if not result["result"]:
                print("Bad response")
                raise "BadResponseException"
            moved += 1
        elif sendBin != rehash_bin:
            print("Something weird happened, check rehashing")
            #print(f"sendBin = {sendBin}")
            #print(f"rehash_bin = {rehash_bin}")
            #print(f"new_server_hash = {new_server_hash}")
            #print(f"new_server_key = {new_server_key}")
        else:
            pass
    print(f"Done rehashing, {moved} entries moved")
    print("Final distribution:")
    inspect_nodes(servers)

def remove_node( cons, numStr, producers, serv ):
    # Determine node details
    server_port = numStr
    del_server_key = f'tcp://127.0.0.1:{server_port}'
    if del_server_key not in serv:
        print("Error, node does not exist")
        raise "NonExistentNodeError"
    print("Deleting node on port " + str(server_port))
    del_server_hash = consistentHash(del_server_key)
    # get binHash
    binHash = dict()
    for s in servers:
        binHash[consistentHash(s)] = s
    binHash.pop(del_server_hash, None)
    # determine bin to migrate to
    next_bucket_name = chooseServerConsistent( del_server_key, binHash )
    # GET ALL from node to delete
    data = { 'op':"GET_ALL", 'key':'', 'value': '' }
    producers[del_server_key].send_json(data)
    result = producers[del_server_key].recv_json()
    if not result["result"]:
        print("Bad response")
        raise "BadResponseException"
    result = result["collection"]
    # Rehash data
    print("Rehashing...")
    moved = 0
    for d in result:
        k = d["key"]
        v = d["value"]
        # put into new server
        data = { 'op':"PUT", 'key': k, 'value': v }
        producers[next_bucket_name].send_json(data)
        result = producers[next_bucket_name].recv_json()
        if not result["result"]:
            print("Bad response")
            raise "BadResponseException"
        moved += 1
    print(f"Done rehashing, {moved} entries moved")
    # Delete references to node
    server_set = set(serv) - set([del_server_key])
    serv = list(server_set)
    producers.pop(del_server_key)
    # Notify consul to take down node
    err = cons.agent.service.deregister(numStr)
    time.sleep(1)
    if not err:
        print("Error deregistering node with consul")
    print("Deletion completed. Final distribution:")
    inspect_nodes(serv)

if __name__ == "__main__":
    c = consul.Consul()
    print("Looking for nodes...")
    servers = []
    initial_services = c.agent.services()
    print(f"{len(initial_services)} nodes found\n")
    for each_server in initial_services:
        server_port = initial_services[each_server]["Port"]
        servers.append(f'tcp://127.0.0.1:{server_port}')
    time.sleep(3)
    
    producers = create_clients(servers)
    print()
    time.sleep(3)

    generate_data_round_robin(servers, producers, sleep_time)
    clearNodes()
    time.sleep(3)

    generate_data_hrw_hashing(servers, producers, numItems, sleep_time)
    clearNodes()
    time.sleep(3)
    
    generate_data_consistent_hashing(servers, producers, numItems, sleep_time)
    #clearNodes()
    time.sleep(3)
    
    add_node( c, "2004", producers, servers )
    time.sleep(3)

    remove_node( c, "2003", producers, servers )

    #print("Terminating services")
    if terminate_services:
        k = c.agent.services().keys()
        for key in k:
            c.agent.service.deregister(key)
    #print("Running services:")
    #print(c.agent.services())
