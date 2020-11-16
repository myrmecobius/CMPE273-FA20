import zmq
from  multiprocessing import Process
import csv

def voting_station_worker():
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://127.0.0.1:4000")
    
    result_sender = context.socket(zmq.PUSH)
    result_sender.connect("tcp://127.0.0.1:3000")
    
    msg = receiver.recv_json()
    region = msg['region']
    print(f'region={region} to count votes')
    result = {}
    # scan file and count votes
    # Count votes from region.cvs
    print(f'Counting {region}...')
    filename = f"votes/{region}.csv"

    result = {
        'region': region,
        'x': 0,
        'y': 0
    }

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            result[row[0]] += 1
    
    print(f'result={result}')
    result_sender.send_json(result)
    print('Finished the worker')
    
    
if __name__ == "__main__":
    voting_station_worker()