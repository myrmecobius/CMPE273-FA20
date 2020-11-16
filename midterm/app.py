import zmq_master
import time
from flask import Flask


app = Flask(__name__)
#final_results = False

@app.route('/')
def root():
    return 'Election 2020', 200

@app.route('/result')
def calculate_result():
    zmq_master.send_to_voting_workers()
    time.sleep(5)
    result = zmq_master.receive_result()
    final_results = result
    return result, 200

    #CACHED VERSION
    '''global final_results
    if not final_results:
        zmq_master.send_to_voting_workers()
        time.sleep(5)
        result = zmq_master.receive_result()
        final_results = result
        return result, 200
    else:
        return final_results, 200'''
    