import json
import requests
import logging
import os
import shutil
import tempfile
import threading
import time
import random
from datetime import datetime


from _thread import start_new_thread
from sseclient import SSEClient
from json import JSONDecodeError
from fastapi import HTTPException
from fastapi.responses import FileResponse
from .config import Ditto_IP, Ditto_PORT
from datetime import datetime

from core.translator import Translator
from core.evidence_provider import EvidenceProvider
from core.util import FileUtils
from .config import MQTT_BROKER_HOST
import ast

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Controller():
    """
    A class implementing the Controller the information flows from and to SDT

    Attributes:
        trs (Translator): Instance of the Translator class.
        ep (EvidenceProvider): Instance of the EvidenceProvider class.
    Methods:
        __init__(self): 
            Initializes the Controller instance.
        create_policy(self): 
            Creates a policy in Ditto.
        create_in_ditto(self, payload, toe_id, level): 
            Creates a Stored representation in Ditto.
        name_thiing_id(self, toe_id, level): 
            Converts a name to an ID by appending the level to the toe_id.
        unique_id(self):
            Generates a unique ID for the thing.
        read_item(self, toe_id, level): 
            Reads an item from Ditto based on the provided ID and level.
        delete_item(self, toe_id, level): 
            Deletes an item from Ditto based on the provided ID and level.
        update_item(self, toe_id, level, payload): 
            Updates an item in Ditto based on the provided ID and payload.
        get_evidence(self, toe_id: str, level: str): 
            Retrieves evidence data based on the provided Target of Evaluation ID and level.
        connection_create(): 
            Creates a mqtt connection to the Ditto server.
        fetch_sync_repo(self, github_url: str): 
            Fetches a repository from GitHub and saves it locally.
    """

    def __init__(self):
        print("SDT-Controller instance created.")
        # Create instances
        self.trs = Translator()
        self.ep = EvidenceProvider()

# =======================Main Methods========================

    def create_policy(self):

        
        try:
            current_dir = os.path.dirname(__file__)
            f = os.path.join(current_dir, 'Policies', 'policy.json')
            logger.info(f"Loading policy from file: {f}")
            
            with open(f, 'r') as json_data:
                payload = json_data.read()
                json_data.close()
                logger.info("Policy file successfully loaded")
        except FileNotFoundError as e:
            logger.error(f"Error: Policy file not found - {e}")
            return None
        except Exception as e:
            logger.error(f"Error while reading policy file: {e}")
            return None

        policy_name = "cobalt:policy"
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/policies/{policy_name}'
        try:
            logger.info(f"Sending policy to Ditto at {url}")
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=json.loads(payload), headers={'Content-Type': 'application/json'})
            
            if r.status_code >= 200 and r.status_code < 300:
                logger.info(f"Policy created successfully. Status code: {r.status_code}")
            else:
                logger.error(f"Failed to create policy. Status code: {r.status_code}, Response: {r.text}")
            
            return r , policy_name
        except JSONDecodeError as e:
            logger.error(f"Error: Invalid JSON in policy file - {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error: Failed to connect to Ditto - {e}")
        except Exception as e:
            logger.error(f"Error while sending policy to Ditto: {e}")
        
        return None
    
    # def create_in_ditto1(self, payload):
    #     self.create_policy()
    #     #return
    #     #print(payload)
    #     #ip = '10.0.1.174'
    #     ip = 'localhost'
    #     port = 8080
    #     url = 'http://' + ip + ':' + str(port) + '/api/2/things/'
    #     try:
    #         print("Send DT model to Ditto!")

    #         session = requests.Session()
    #         session.auth = ("ditto", "ditto")
    #         r = session.post(url, json=json.loads(payload), headers={'Content-Type': 'application/json'})
    #         print(r.json())
    #         return r

    #         # session = requests.Session()
    #         # session.auth = ("ditto", "ditto")
    #         # r = session.post("http://10.0.1.174:8080/api/2/things/", json=payload, headers={'Content-Type': 'application/json'})
    #         # thing_id = payload["thingId"]
    #         # r = session.put("http://10.0.1.174:8080/api/2/things/"+thing_id, json=payload, headers={'Content-Type': 'application/json'})

    #     except Exception as e:
    #         print(e)
    #     return None

    def create_in_ditto(self, payload, toe_id ,payload_type):

        
        # if toe_id is None and level is None:
        #     ctrl_id = self.define_thing_id(toe_id, level)
        # else:
        #     ctrl_id = self.name_thiing_id(toe_id, level)

        ctrl_id = self.name_thiing_id(toe_id, payload_type)
        

        payload_json = json.loads(payload)
        payload_json["thingId"] = ctrl_id

        logger.info(f"Controller attaching thing ID: {payload_json['thingId']}")
        logger.info("Creating policy in Ditto")

        policy_response, policy_name = self.create_policy()
        print(policy_response)
        payload_json["policyId"] = policy_name
        logger.info(f"Policy ID: {payload_json['policyId']} attached to thing ID: {payload_json['thingId']}")
        # logger.info(f"Creating thing with ID: {ctrl_id}")
        print(payload_json)

        try:

            thing_id = ctrl_id
            # print(thing_id)
            if not thing_id:
                logger.error("ThingId not found in payload")
                return {"success": False, "error": "ThingId not found in payload"}
            
            logger.info(f"Creating thing with ID: {thing_id}")
            url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{thing_id}'
            # print(url)
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=payload_json, headers={'Content-Type': 'application/json'})
            
            response_data = r.json() if r.text else {}
            logger.info(f"Ditto response status: {r.status_code}")
            
            return {
                "success": 200 <= r.status_code < 300,
                "status_code": r.status_code,
                "response": response_data
            }
        except JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            return {"success": False, "error": f"Invalid JSON: {str(e)}"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating thing in Ditto: {e}")
            return {"success": False, "error": str(e)}

    # def name_thiing_id(self,toe_id, payload_type): # convert a name to an ID by appending the level to the toe_id
    #     """
    #     Convert a name to an ID by appending the level to the toe_id.
    #     """
    #     # tid_12345678.ai:1234567887498749

    #     return "tid_" + str(toe_id) + "." + str(payload_type) + ":" + self.unique_id()

    def name_thiing_id(self, toe_id, payload_type):
        """
        Convert a name to a Ditto-compatible ID following Eclipse Ditto naming rules.
        
        - namespace part must be DNS-like (e.g., 'org.eclipse.ditto')
        - name part comes after the colon (':')
        
        Args:
            toe_id (str): Target of Evaluation ID
            payload_type (str): Type of payload (e.g., 'AI', 'QDT')
            
        Returns:
            str: A properly formatted Ditto Thing ID
        """
        # Create a proper namespace (DNS-like format)
        namespace = "cobalt.sdt"
        
        # Create a name using toe_id, payload_type, and a unique identifier
        unique_suffix = self.unique_id()
        name = f"toe-{toe_id}-{payload_type}-{unique_suffix}"
        
        # Return in namespace:name format
        return f"{namespace}:{name}"


    def unique_id(self):
        """
        Generate a unique ID for the thing.
        """
        # Generate a unique ID (e.g., using UUID or any other method)
        # For simplicity, using a random number here

        return str(''.join(filter(str.isdigit, datetime.now().isoformat())))+"-"+str(random.randint(1000000000, 9999999999))
        
    def read_item(self, item_id):

    
        logger.info(f"Attempting to read thing with ID: {item_id}")
        
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{item_id}'
        
        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            logger.info(f"Sending GET request to {url}")
            r = session.get(url, headers={'accept': 'application/json'})
            
            if r.status_code == 200:
                try:
                    response_json = r.json()
                    logger.info(f"Successfully retrieved thing with ID: {item_id}")
                    # logger.info(f"Response data: {response_json}")
                    return response_json  # Return the response data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return None
            else:
                logger.error(f"Error retrieving item: Status code {r.status_code}")
                return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while reading thing: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading thing from Ditto: {e}")
            return None
        
    # def search_item(self, toe_id, level):

        
    #     item_id = "tid_" + str(toe_id) + "." + str(level)

    #     logger.info(f"Attempting to read thing with ID: {item_id}")

    #     url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/search/things?fields=thingId&filter=like(thingId,"{item_id}:*")'
        
    #     try:
    #         session = requests.Session()
    #         session.auth = ("ditto", "ditto")
    #         logger.info(f"Sending GET request to {url}")
    #         r = session.get(url, headers={'accept': 'application/json'})
            
    #         # print("************")
    #         if r.status_code == 200:
    #             try:
    #                 response_json = r.json()
    #                 logger.info(f"Successfully retrieved thingID of: {item_id}")
    #                 logger.info(f"Response data: {response_json}")
    #                 thingid = response_json["items"][0]["thingId"]
    #                 # print(response_json)
    #                 # print(response_json["items"][0]["thingId"])
    #                 return thingid  # Return the response data
    #             except json.JSONDecodeError as e:
    #                 logger.error(f"JSON decode error: {e}")
    #                 return None
    #         else:
    #             logger.error(f"Error retrieving item: Status code {r.status_code}")
    #             return None
    #     except requests.exceptions.ConnectionError as e:
    #         logger.error(f"Connection error while reading thing: {e}")
    #         return None
    #     except Exception as e:
    #         logger.error(f"Error reading thing from Ditto: {e}")
    #         return None

    def search_item(self, toe_id, level):
        """
        Search for a Thing in Ditto based on toe_id and level.
        
        Args:
            toe_id (str): Target of Evaluation ID
            level (str): Level of thing to search for
            
        Returns:
            str: Thing ID if found, None otherwise
        """
        namespace = "cobalt.sdt"
        
        logger.info(f"Searching for thing with toe_id: {toe_id}, level: {level}")
        
        # Search pattern: look for things with namespace:toe-{toe_id}-{level}* pattern
        item_id = f"{namespace}:toe-{toe_id}-{level}"
        
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/search/things?filter=like(thingId,"{item_id}*")&fields=thingId'
        
        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            logger.info(f"Sending GET request to {url}")
            r = session.get(url, headers={'accept': 'application/json'})
            
            if r.status_code == 200:
                try:
                    response_json = r.json()
                    logger.info(f"Successfully retrieved things matching pattern: {item_id}")
                    logger.info(f"Response data: {response_json}")
                    
                    # Check if items were found
                    if response_json.get("items") and len(response_json["items"]) > 0:
                        thingid = response_json["items"][0]["thingId"]
                        return thingid
                    else:
                        logger.info(f"No things found matching pattern: {item_id}")
                        return None
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return None
            else:
                logger.error(f"Error retrieving items: Status code {r.status_code}")
                return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while searching for thing: {e}")
            return None
        except Exception as e:
            logger.error(f"Error searching for thing in Ditto: {e}")
            return None


    def delete_item(self, toe_id, level):

        
        # Use name_thiing_id function to generate the proper item ID
        item_id = self.name_thiing_id(toe_id, level)
        logger.info(f"Attempting to delete thing with ID: {item_id}")
        
        # First verify the item exists before trying to delete
        existing_item = self.read_item(toe_id, level)
        if not existing_item:
            logger.error(f"Thing with ID {item_id} does not exist and cannot be deleted")
            return {"success": False, "error": "Thing does not exist"}
        
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{item_id}'
        
        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.delete(url)
            
            # Check if response is successful (2xx status code)
            if 200 <= r.status_code < 300:
                # Verify deletion by checking if the thing still exists
                verification = self.read_item(toe_id, level)
                if verification is None:
                    logger.info(f"Thing with ID {item_id} was successfully deleted")
                    return {"success": True, "status_code": r.status_code, "message": "Thing deleted successfully"}
                else:
                    logger.error(f"Thing with ID {item_id} still exists after deletion attempt")
                    return {"success": False, "error": "Thing still exists after deletion attempt"}
            else:
                logger.error(f"Failed to delete thing. Status code: {r.status_code}, Response: {r.text}")
                return {"success": False, "status_code": r.status_code, "error": r.text}
                    
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting thing in Ditto: {e}")
            return {"success": False, "error": str(e)}
    
    def update_item(self, item_id, payload):

        # payload_json = json.loads(payload)
        print("payload000000000000000000000000000000000000000000")
        print(payload)
        # Use name_thiing_id function to generate the proper item ID
        # item_id = self.name_thiing_id(toe_id, level)
        logger.info(f"Updating thing with ID: {item_id}")
        
        # Check if the item exists using read_item
        # existing_item = self.read_item(toe_id, level)
        
        # if not existing_item:
        #     logger.error(f"Thing with ID {item_id} does not exist and cannot be updated")
        #     return {"success": False, "error": "Thing does not exist"}
        
        try:
            # Parse the payload if it's a string
            payload_json = payload if isinstance(payload, dict) else json.loads(payload)
            
            # Set the thing ID in the payload
            # payload_json["thingId"] = item_id
            
            # Get policy ID from existing item
            # policy_id = payload_json.get("policyId")
            # if policy_id:
            #     payload_json["policyId"] = policy_id
            #     logger.info(f"Using existing policy ID: {policy_id}")
            # else:
            #     # If policy cannot be obtained, create a new one
            #     logger.info("Existing policy not found, creating a new one")
            policy_response, policy_name = self.create_policy()
            payload_json["policyId"] = policy_name
            
            # Perform the update
            url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{item_id}'
            
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=payload_json, headers={'Content-Type': 'application/json'})
            
            response_data = r.json() if r.text else {}
            logger.info(f"Ditto update response status: {r.status_code}")
            
            return {
                "success": 200 <= r.status_code < 300,
                "status_code": r.status_code,
                "response": response_data
            }
        except JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            return {"success": False, "error": f"Invalid JSON: {str(e)}"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating thing in Ditto: {e}")
            return {"success": False, "error": str(e)}
        

    def compare_items(self, item_id1, payload2):
        """
        Compares two items in Ditto based on their IDs.
        
        Args:
            item_id1 (str): The ID of the first item.
            item_id2 (str): The ID of the second item.
            
        Returns:
            bool: True if the items are equal, False otherwise.
        """
        # logger.info(f"Comparing items {item_id1} and {item_id2}")
        print("============OLD==============")
        payload1 = self.read_item(item_id1)
        print(payload1)
        item1_last_modified = payload1.get("features", {}).get("repository", {}).get("properties", {}).get("last_commit", {})
        print(item1_last_modified)
        print("=============NEW=============")
        # Convert payload2 to JSON if it's a string
        if isinstance(payload2, str):
            payload2 = json.loads(payload2)
        print(payload2)
        item2_last_modified = payload2.get("features", {}).get("repository", {}).get("properties", {}).get("last_commit", {})
        print(item2_last_modified)

        return item1_last_modified == item2_last_modified



    def get_evidence(self, toe_id: str, level: str, thing_id= None , notify=False):
        """
        Retrieves evidence data based on the provided Target of Evaluation ID and level.
        
        Args:
            toeid (str): The Target of Evaluation ID.
            level (str): The level of evidence to retrieve.
            
        Returns:
            FileResponse or dict: A FileResponse with zip file if level is 'toe.ai',
                                  otherwise a dict with an error message.
        """
        logger.info(f"Retrieving evidence for toe_id: {toe_id}, level: {level}")
        # Check if thing_id is provided, if not, search for it
        if thing_id is None:
            thing_id = self.search_item(toe_id, level)

        thing_with_repo = self.read_item(thing_id)
        print(thing_with_repo)
        # print("************")
        logger.info(f"Retrieved thing with repository for toe_id: {toe_id}")
        
        if toe_id is None and level is None:
            toe_id = thing_with_repo.get("attributes", {}).get("toe_id")
            level = thing_with_repo.get("attributes", {}).get("category")
        logger.info(f"Using toe_id: {toe_id} and level: {level} from thing")
        evidence_template = self.ep.process_query(toe_id, level, thing_with_repo) # no change
        
        # print(evidence_dir)
        if evidence_template.get('evidence_type') == "repository":
            evidence_dir = thing_with_repo.get('attributes', {}).get('github')
            logger.info(f"Processed query, evidence directory: {evidence_dir}")

            # Check if evidence directory exists
            if not os.path.exists(evidence_dir):
                logger.error(f"Evidence directory not found: {evidence_dir}")
                return {"error": "No evidence directory found"}
        
            # Create a zip file of the entire evidence directory
            if notify == False:
                try:
                    # Return the zip file as a response
                    if evidence_template.get('evidence_format') == "zip":
                        # If file-by-file, return the zip file
                        return FileUtils.zip_response(evidence_dir, toe_id)

                except Exception as e:
                    logger.error(f"Failed to create evidence zip: {str(e)}")
                    return {"error": f"Failed to create evidence zip: {str(e)}"}
            else:
                response = self.ep.notification_push_AI(evidence_dir, toe_id)
                logger.info(f"AI evidences notification status: {response}")
                return response
            
        elif evidence_template.get('evidence_type') == "paths":
            # Extract file_name from evidence_template
            file_name = evidence_template.get('file_name')
            # If file_name is a list, take the first element
            if isinstance(file_name, list) and file_name:
                file_name = file_name[0]
            # For debugging
            # print("************")
            # print(f"File name: {file_name}")
            if not file_name:
                logger.error("No file name provided in evidence template")
                return {"error": "No file name specified for evidence retrieval"}

            # Extract the repository file tree from the thing entity
            repo_file_tree = thing_with_repo.get('features', {}).get('Repository_file_tree', {}).get('properties', {})
            print("************")
            print(repo_file_tree)
            # Initialize evidence_dir to None
            evidence_dir = None

            # Iterate through the repository file tree
            for _, file_info in repo_file_tree.items():
                # Check if this entry's name matches the file_name we're looking for
                if isinstance(file_info, dict) and file_info.get('name') == file_name:
                    evidence_dir = file_info.get('path')
                    logger.info(f"Found matching file '{file_name}' at path: {evidence_dir}")
                    break # Exit the loop once we find the file

            # If we reach here, the file wasn't found
            if not evidence_dir:
                logger.error(f"File '{file_name}' not found in repository file tree")
                return {"error": f"File '{file_name}' not found in repository"}
        
            logger.info(f"Processed query, evidence directory: {evidence_dir}")

            # Check if evidence directory exists
            if not os.path.exists(evidence_dir):
                logger.error(f"Evidence directory not found: {evidence_dir}")
                return {"error": "No evidence directory found"}
            

            # Create a zip file of the entire evidence directory
            if notify == False:
                try:
                    return FileUtils.file_response(evidence_dir, file_name)
                except Exception as e:
                    logger.error(f"Failed to create evidence zip: {str(e)}")
                    return {"error": f"Failed to create evidence zip: {str(e)}"}
            else:
                response = self.ep.notification_push_QDT(evidence_dir)
                logger.info(f"QDT evidences notification status: {response}")
                return response

    def connection_create(self, custom_config=None):
        """
        Creates a connection to the Ditto server using configuration from a JSON file
        or a provided configuration.
        
        Args:
            custom_config (dict, optional): Custom connection configuration.
                                        If provided, will use this instead of loading from file.
        
        Returns:
            dict: The response from the connection creation request.
        """

        
        try:
            # Use custom config if provided, otherwise load from file
            if custom_config is not None:
                payload = custom_config
                logger.info("Using provided custom connection configuration")
            else:
                # Load full payload configuration from JSON file
                current_dir = os.path.dirname(__file__)
                connection_file = os.path.join(current_dir, 'Connections', 'connection.json')
                logger.info(f"Loading connection configuration from: {connection_file}")
                
                with open(connection_file, 'r') as json_data:
                    payload_str = json_data.read()
                    # Replace theMQTT_BROKER_HOST placeholder with actual value from config
                    payload_str = payload_str.replace("{{MQTT_BROKER_HOST}}",MQTT_BROKER_HOST)
                    payload = json.loads(payload_str)
                    logger.info(f"Connection configuration loaded and substituted MQTT broker IP: {MQTT_BROKER_HOST}")
            
            # Send the request - using 10000ms timeout as specified
            url = f'http://{Ditto_IP}:{Ditto_PORT}/devops/piggyback/connectivity?timeout=1'
            session = requests.Session()
            session.auth = ("devops", "foobar")
            
            logger.info(f"Sending connection creation request to {url}")
            response = session.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            # print(respons)
            if response.status_code >= 200 and response.status_code < 300:
                logger.info("Connection created successfully")

                return {"success": True, "response": response.json() if response.text else {}}
            else:
                logger.error(f"Failed to create connection. Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "error": response.text}
                
        except FileNotFoundError:
            error_msg = f"Connection configuration file not found: {connection_file}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in connection configuration: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error creating connection: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
    # def listen_to_ditto(self):
    #     url = 'http://ditto:ditto@' + Ditto_IP + ':' + Ditto_PORT + '/api/2/things'
    #     print("Connecting to Ditto SSE at:", url)
    #     try:
    #         messages = SSEClient(url)
    #         print("SSEClient connected, waiting for messages...")
    #         for msg in messages:
    #             print("*************************************Ditto Listener*******************************")
    #             outputMsg = msg.data
    #             print("Raw SSE message:", outputMsg)
    #             if type(outputMsg) is str and len(outputMsg) > 0:
    #                 try:
    #                     outputJS = json.loads(outputMsg)
    #                     print("*****Ditto Listener**000000")
    #                     print(outputJS.get('thingId'))
    #                     self.get_evidence(toe_id=None, level=None, thing_id=outputJS.get('thingId'), notify=True)
    #                 except Exception as e:
    #                     print("Error parsing SSE message:", e)
    #     except Exception as e:
    #         print("Failed to connect to Ditto SSE:", e)


    def listen_to_ditto(self):
        import paho.mqtt.client as mqtt

        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT broker with result code", rc)
            client.subscribe("ditto-cobalt/#")

        def on_message(client, userdata, msg):
            print("*************************************Ditto MQTT Listener*******************************")
            print(f"Topic: {msg.topic}")
            try:
                payload = msg.payload.decode()
                print("Raw MQTT message:", payload)
                outputJS = json.loads(payload)

                # Check if this is a deletion event by inspecting the topic
                topic = outputJS.get('topic', '')
                if '/events/deleted' in topic:
                    print("Deletion event detected - ignoring")
                    return

                thing = outputJS.get('value', {})
                thing_id = thing.get('thingId')
                attributes = thing.get('attributes', {})
                toe_id = attributes.get('toe_id')
                level = attributes.get('category')
                print(f"thing_id: {thing_id}, toe_id: {toe_id}, level: {level}")
                self.get_evidence(toe_id=toe_id, level=level, thing_id=thing_id, notify=True)
            except Exception as e:
                print("Error parsing MQTT message:", e)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(localhost, 1883, 60)
        client.loop_forever()

    def run_ditto_listener(self):
        """It starts a new thread invoking method run_default()

        """
        try:
            start_new_thread(self.listen_to_ditto, ())
        except Exception as e:
            print("ERROR:{}".format(e))
    
#==========================Demo Methods==========================

    def sync_connector_AI(self, github_url: str, toe_id, level): # Hardcoding the URL for now
        """
        Fetches a repository from GitHub and saves it locally.
        
        Args:
            github_url (str): The URL of the GitHub repository to fetch.
            
        Returns:
            str: The local path where the repository is saved.
        """


        try:
            # Clone the repository using git
            repo_path_thing = self.trs.fetch_push_save_repo(github_url)
            # print("******************")
            print(repo_path_thing)
            logger.info(f"Repository cloned successfully")
            

            # Load the thing file from the cloned repository
            response = self.create_in_ditto(repo_path_thing, toe_id, level)
            print(response)
            print("repo")

            return response
        except Exception as e:
            logger.error(f"Error fetching repository: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch repository")
        return None
    
    def sync_connector_QDT(self, github_url: str, toe_id, level): # Hardcoding the URL for now
        """
        Fetches a repository from GitHub and saves it locally.
        
        Args:
            github_url (str): The URL of the GitHub repository to fetch.
            
        Returns:
            str: The local path where the repository is saved.
        """

        
        try:
            # Clone the repository using git
            repo_path_thing = self.trs.fetch_push_save_repo(github_url)
            logger.info(f"Repository cloned successfully")

            # Load the thing file from the cloned repository
            response = self.create_in_ditto(repo_path_thing, toe_id, level)
            

            return response
        except Exception as e:
            logger.error(f"Error fetching repository: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch repository")
        return None

    def sync_connector(self, github_url: str, toe_id, level): # Hardcoding the URL for now
        """
        Fetches a repository from GitHub and saves it locally.
        
        Args:
            github_url (str): The URL of the GitHub repository to fetch.
            
        Returns:
            str: The local path where the repository is saved.
        """


        try:
            # Clone the repository using git
            repo_path_thing = self.trs.fetch_push_save_repo(toe_id, level, github_url)
            # print("******************")
            # print(repo_path_thing)
            logger.info(f"Repository Thing created")
            thingid = self.search_item(toe_id, level)
            print(thingid)
            print("*************************COMPARE*******")
            if thingid is not None:
                # print("************")
                logger.info(f"Item already exists")
                #============================= to implement the last modification condition through compare function
                # Compare the existing item with the new one
                if self.compare_items(thingid, repo_path_thing):
                    logger.info(f"Items are equal, no update needed")
                    return {"success": True, "message": "Items are equal, no update needed"}
                else:
                    logger.info(f"Items are not equal, updating")
                    # Update the existing item
                    response = self.update_item(thingid, repo_path_thing)
                    print(response)
                    return {"success": False, "error": "Item already exists"}
            else:
                # Load the thing file from the cloned repository
                response = self.create_in_ditto(repo_path_thing, toe_id, level)
                print(response)
                print("repo")

            return response
        except Exception as e:
            logger.error(f"Error fetching repository: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch repository")
        return None  

    def start_update_sync(self, github_url: str, toe_id, level):
            """
            Starts a sync of a GitHub repository at specified intervals.
            
            Args:
                github_url (str): The URL of the GitHub repository to fetch.
                interval (int): Time between syncs in seconds (default: 1 hour).
                
            Returns:
                dict: Information about the started sync process
            """
            
            # Function that runs in background thread
            # def sync_periodically():
            #     while True:
            try:
                logger.info(f"Running scheduled sync for repository: {github_url}")
                # Use the existing sync_connector implementation
                result = self.sync_connector(github_url, toe_id, level)
                logger.info(f"Scheduled sync completed with result: {result}")
                return result
            except Exception as e:
                logger.error(f"Error in scheduled sync: {e}")
                return "fail"
        #         # Wait for next sync
        #         logger.info(f"Waiting {interval} seconds for next sync")
        #         time.sleep(interval)
        
        # # Store thread reference as instance variable so it doesn't get garbage collected
        # if not hasattr(self, '_sync_threads'):
        #     self._sync_threads = {}
        
        # # Generate a unique ID for this sync job
        # thread_id = f"sync_{github_url.split('/')[-1].replace('.git', '')}"
        
        # # Check if sync is already running for this repo
        # if thread_id in self._sync_threads and self._sync_threads[thread_id].is_alive():
        #     return {
        #         "success": False,
        #         "message": f"Sync is already running for {github_url}",
        #         "thread_id": thread_id
        #     }
        
        # # Create and start the thread
        # sync_thread = threading.Thread(target=sync_periodically, daemon=True)
        # sync_thread.start()
        
        # # Store thread reference
        # self._sync_threads[thread_id] = sync_thread
        
        # return 
        # {
        #     "success": True,
        #     "message": f"Started periodic sync for {github_url} with interval of {interval} seconds",
        #     "thread_id": thread_id
        # }

    # def start_periodic_sync(self, github_url: str, toe_id, level , interval: int = 3600):
    #     """
    #     Starts a periodic sync of a GitHub repository at specified intervals.
        
    #     Args:
    #         github_url (str): The URL of the GitHub repository to fetch.
    #         interval (int): Time between syncs in seconds (default: 1 hour).
            
    #     Returns:
    #         dict: Information about the started sync process
    #     """
        
    #     # Function that runs in background thread
    #     def sync_periodically():
    #         while True:
    #             try:
    #                 logger.info(f"Running scheduled sync for repository: {github_url}")
    #                 # Use the existing sync_connector implementation
    #                 result = self.sync_connector(github_url, toe_id, level)
    #                 logger.info(f"Scheduled sync completed with result: {result}")
    #             except Exception as e:
    #                 logger.error(f"Error in scheduled sync: {e}")
                
    #             # Wait for next sync
    #             logger.info(f"Waiting {interval} seconds for next sync")
    #             time.sleep(interval)
        
    #     # Store thread reference as instance variable so it doesn't get garbage collected
    #     if not hasattr(self, '_sync_threads'):
    #         self._sync_threads = {}
        
    #     # Generate a unique ID for this sync job
    #     thread_id = f"sync_{github_url.split('/')[-1].replace('.git', '')}"
        
    #     # Check if sync is already running for this repo
    #     if thread_id in self._sync_threads and self._sync_threads[thread_id].is_alive():
    #         return {
    #             "success": False,
    #             "message": f"Sync is already running for {github_url}",
    #             "thread_id": thread_id
    #         }
        
    #     # Create and start the thread
    #     sync_thread = threading.Thread(target=sync_periodically, daemon=True)
    #     sync_thread.start()
        
    #     # Store thread reference
    #     self._sync_threads[thread_id] = sync_thread
        
    #     return {
    #         "success": True,
    #         "message": f"Started periodic sync for {github_url} with interval of {interval} seconds",
    #         "thread_id": thread_id
    #     }
    
    # def stop_periodic_sync(self, thread_id: str):
    #     """
    #     Note: This doesn't actually stop the thread (Python doesn't support thread termination),
    #     but it allows the thread to be garbage collected when it completes its current cycle.
        
    #     Args:
    #         thread_id (str): ID of the thread to stop
            
    #     Returns:
    #         dict: Result of the operation
    #     """
    #     if not hasattr(self, '_sync_threads'):
    #         return {"success": False, "message": "No sync jobs are running"}
        
    #     if thread_id in self._sync_threads:
    #         del self._sync_threads[thread_id]
    #         return {"success": True, "message": f"Sync job {thread_id} will terminate after current cycle"}
    #     else:
    #         return {"success": False, "message": f"No sync job found with ID {thread_id}"}
    
    # # def list_periodic_syncs(self):
    #     """
    #     Lists all running periodic sync jobs.
        
    #     Returns:
    #         dict: Information about running jobs
    #     """
    #     if not hasattr(self, '_sync_threads'):
    #         return {"running_syncs": {}}
        
    #     return {
    #         "running_syncs": {
    #             thread_id: {"alive": thread.is_alive()} 
    #             for thread_id, thread in self._sync_threads.items()
    #         }
    #     }