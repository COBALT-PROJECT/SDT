import json

import requests


class Controller():
    """
    A class implementing the adapter to translate different data models to the DT model and vice-versa.

    ...

    Attributes
    ----------
    __source_file : String
        a String defining...

    Methods
    -------
    translate(s, t, model)
        Method to...

    """

    def __init__(self):
        print("New DTModelAdapter instance created.")

    def __create_policy(self):
        try:
            f = 'test_files/policy.json'
            with open(f, 'r') as json_data:
                #payload = json.loads(json_data.read())
                payload = json_data.read()
                json_data.close()
                print(payload)
        except Exception as e:
            print(e)
        #return
        #ip = '10.0.1.174'
        ip = '10.0.0.41'
        port = 8080
        url = 'http://' + ip + ':' + str(port) + '/api/2/policies/cobalt:policy'
        try:
            print("Send policy to Ditto!")
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=json.loads(payload), headers={'Content-Type': 'application/json'})
            print(r.json())
            return r
        except Exception as e:
            print(e)
        return None

    def create_in_ditto(self, payload):
        self.__create_policy()
        #return
        #print(payload)
        #ip = '10.0.1.174'
        ip = 'localhost'
        port = 8080
        url = 'http://' + ip + ':' + str(port) + '/api/2/things/'
        try:
            print("Send DT model to Ditto!")

            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.post(url, json=json.loads(payload), headers={'Content-Type': 'application/json'})
            print(r.json())
            return r

            # session = requests.Session()
            # session.auth = ("ditto", "ditto")
            # r = session.post("http://10.0.1.174:8080/api/2/things/", json=payload, headers={'Content-Type': 'application/json'})
            # thing_id = payload["thingId"]
            # r = session.put("http://10.0.1.174:8080/api/2/things/"+thing_id, json=payload, headers={'Content-Type': 'application/json'})

        except Exception as e:
            print(e)
        return None

    def update_in_ditto(self, payload):
        #print(payload)
        #ip = '

        return 
