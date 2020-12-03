import zmq
import time
import consul
from  multiprocessing import Process

def server(port):
    context = zmq.Context()
    consumer = context.socket(zmq.REP)
    consumer.connect(f"tcp://127.0.0.1:{port}")
    data = dict()
    
    while True:
        raw = consumer.recv_json()
        op, key, value = raw['op'], raw['key'], raw['value']
        #print(f"Server_port={port}:key={key},value={value}")

        if op == "PUT":
            data[key] = value
            print(f"Saved value {data[key]} in key {key} on node {port}")
            result = {"result":True}
            consumer.send_json(result)
            print("Reply sent")
        elif op == "GET_ONE":
            result = {"result":bool(data.get(key,False)), "key":key, "value":data.get(key,False)}
            consumer.send_json(result)
            print("Replied with data " + result + f"on node {port}")
        elif op == "GET_ALL":
            result = []
            for key in data.keys():
                result.append({"key":key, "value":data[key]})
            res = {"result":True, "collection":result}
            consumer.send_json(res)
            print(f"Replied with all data from node {port}")
        elif op == "DELETE":
            data.pop(key, None)
            result = {"result":True}
            consumer.send_json(result)
            print(f"Deleted entry on node {port}")
        elif op == "DELETE_ALL":
            print("Clearing contents on port " + str(port))
            data = dict()
            result = {"result":True}
            consumer.send_json(result)
            print(f"Deleted all entries from node {port}")
        else:
            result = {"result":False}
            consumer.send_json(result)
            print(f"An Error occurred on node {port}")
            pass

        print()

if __name__ == "__main__":
    c = consul.Consul()
    thread_dict = dict()
    initial_servers = c.agent.services()
    for service in initial_servers.keys():
        server_port = initial_servers[service]["Port"]
        print(f"Starting a server at:{server_port}...")
        thread_dict[service] = Process(target=server, args=(server_port,))
        thread_dict[service].start()
    num_threads = len(thread_dict)
    print()

    while True:
        if len(c.agent.services()) == num_threads: # no change
            time.sleep(1)
            continue

        elif len(c.agent.services()) < num_threads: # service ended
            have = set(thread_dict.keys())
            want = set(c.agent.services().keys())
            diff = list(have - want)
            for key in diff:
                thread_dict[key].terminate()
                thread_dict.pop(key, None)
                print(f"Terminating server at :{key}...\n")
            num_threads = len(thread_dict)

        elif len(c.agent.services()) > num_threads: # new service started
            have = set(thread_dict.keys())
            want = set(c.agent.services().keys())
            diff = list(want - have)
            for key in diff:
                server_port = c.agent.services()[key]["Port"]
                thread_dict[key] = Process(target=server, args=(server_port,))
                thread_dict[key].start()
                print(f"Starting a server at:{server_port}...\n")
            num_threads = len(thread_dict)

