import json
from sseclient import SSEClient

ditto_ip = '127.0.0.1:8080'

def listen_to_digitaltwins():
    # bCreateATCar = True
    url = 'http://ditto:ditto@' + ditto_ip + '/api/2/things'
    print(url)
    messages = SSEClient(url)
    for msg in messages:
        outputMsg = msg.data
        print(outputMsg)
        if type(outputMsg) is str and len(outputMsg) > 0:
            outputJS = json.loads(outputMsg)
            print(outputJS['thingId'])

listen_to_digitaltwins()