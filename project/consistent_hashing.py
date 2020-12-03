import time

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

def generate_data_consistent_hashing(servers, producers, numItems, st):
    print("Starting Consistent Hashing...")
    binHash = dict()
    for s in servers:
        binHash[consistentHash(s)] = s
    counts = dict()
    for num in range(numItems):
        data = { 'op':"PUT", 'key': f'key-{num}', 'value': f'value-{num}' }
        sendBin = chooseServerConsistent( data["key"], binHash )
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
