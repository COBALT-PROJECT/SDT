import json
import requests
import os

class Controller():
    """
    A class implementing the Controller to send the translated data from adaptor to eclipse ditto.

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
        print("Controller instance created.")
        #we are gonna set ip for url call to dockergateway because this is the equivalent to localhost:8080, the container docker_gateway_1 of ditto was bound to port 8080 of the ubuntu VM.
        self.ip = os.getenv("DITTO_HOST", "docker_nginx_1")
        self.port = 80

    def __create_policy(self):
        try:
            f = 'test_files/policy.json'
            with open(f, 'r') as json_data:
                #payload = json.loads(json_data.read())
                payload = json_data.read()
                json_data.close()
                # print(payload)
        except Exception as e:
            print(e)
        #return
        #ip = '10.0.1.174'
        #ip = '10.0.0.41'
        #port = 8080
        url = f"http://{self.ip}:{self.port}/api/2/policies/cobalt:policy"
        #url = 'http://' + ip + ':' + str(port) + '/api/2/policies/cobalt:policy'
        try:
            print("Send policy to Ditto!")
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=json.loads(payload), headers={'Content-Type': 'application/json'})
            # print(r.json())
            return r
        except Exception as e:
            print(e)
        return None
    
    def create_in_ditto1(self, payload):
        self.__create_policy()
        #return
        #print(payload)
        #ip = '10.0.1.174'
        #ip = 'localhost'
        #port = 8080
        #url = 'http://' + ip + ':' + str(port) + '/api/2/things/'
        url = f"http://{self.ip}:{self.port}/api/2/things/"
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

    def create_in_ditto(self, payload):
        self.__create_policy()
        thing_id = json.loads(payload).get("thingId")
        print(thing_id)
        if not thing_id:
            print("ThingId not found in payload")
            return None
        
        # ditto_response = check_thing_exists(thing_id)
        # if ditto_response = ok:
        #     print ("Thing already exists in Ditto")
        #     print("updating Thing in ditto")
        # else:
        #     print("Send Thing to Ditto!")


        #ip = 'localhost'
        #port = 8080
        #url = f'http://{ip}:{port}/api/2/things/{thing_id}'
        url = f"http://{self.ip}:{self.port}/api/2/things/"
        try:
            print("Send DT model to Ditto!")
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=json.loads(payload), headers={'Content-Type': 'application/json'})
            print(r.json())
            return r
        except Exception as e:
            print(e)
        return None

# def check_thing_exists(thing_id):
#     ip = 'localhost'
#     port = 8080 
#     url = f'http://{ip}:{port}/api/2/things/{thing_id}'
#     session = requests.Session()
#     session
#     r = session.get(url)
#     print(r.json())
#     return r


#     # def update_in_ditto(self, payload):
#     #     #print(payload)
#     #     #ip = '

#     #     return 


