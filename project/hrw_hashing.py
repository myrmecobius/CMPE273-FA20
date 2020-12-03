import time

def toInt( someString ): #convert string to int by concatenating int of each char
    result = ""
    for c in someString:
        result += str(ord(c))
    return int(result)

def weight( keyStr, servStr ): # Hashing for HRW hashing
    keyInt = toInt( keyStr ) % 3600
    servInt = toInt ( servStr ) % 3600
    a = 1492
    b = 2207
    result = (a * pow( (a * servInt + b), keyInt, 3600) + b) % 3600
    return result

def chooseServerHRW( keyStr, serverList ): #choose server for HRW hashing
    serverHash = dict()
    weights = []
    for s in serverList:
        w = weight( keyStr, s )
        serverHash[w] = s
        weights.append(w)
    #print(f"weights are {serverHash}, choosing {max(weights)} corresponding to {serverHash[max(weights)]}")
    return serverHash[max(weights)]


def generate_data_hrw_hashing(servers, producers, numItems, st):
    print("Starting HRW Hashing...")
    counts = dict()
    for num in range(numItems):
        data = { 'op': "PUT", 'key': f'key-{num}', 'value': f'value-{num}' }
        sendBin = chooseServerHRW( data["key"], servers )
        #print(f"Sending data:{data} to bin {sendBin}")
        #print()
        producers[sendBin].send_json(data)
        result = producers[sendBin].recv_json()
        if not result["result"]:
            print("Bad response")
            raise "BadResponseException"
        countsKey = sendBin.split(":")[-1]
        if not counts.get(countsKey):
            counts[countsKey] = 1
        else:
            counts[countsKey] += 1
        time.sleep(st)
    print(f"Done. Number of items sent to bin: {counts}")
    print()