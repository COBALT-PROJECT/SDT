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
import hashlib
import traceback
from datetime import datetime

from _thread import start_new_thread
from sseclient import SSEClient
from json import JSONDecodeError
from fastapi import HTTPException
from fastapi.responses import FileResponse
from .config import Ditto_IP, Ditto_PORT
from datetime import datetime
import paho.mqtt.client as mqtt

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
        
        # ==================== Bearer Token Management ====================
        # Reference to token store from sdt_interface-2.py
        self.token_store = None

# =======================Bearer Token Methods========================

    def set_token_store(self, token_store_dict):
        """
        Set reference to the token store from sdt_interface-2.py.
        
        Args:
            token_store_dict: Dictionary containing OAuth2 token from SDT-Manager
        """
        self.token_store = token_store_dict
        if token_store_dict and token_store_dict.get("access_token"):
            logger.info(f"Token store updated for SDT {token_store_dict.get('sdt_id')}")
    
    def get_auth_headers(self):
        """
        Get Authorization header with Bearer token for IDS-Connector requests.
        
        Returns:
            dict: Headers dict with Bearer token, or empty dict if no token available
        """
        if self.token_store and self.token_store.get("access_token"):
            token = self.token_store.get("access_token")
            return {"Authorization": f"Bearer {token}"}
        
        return {}
    
    def has_bearer_token(self):
        """
        Check if Bearer token is available for IDS-Connector authentication.
        
        Returns:
            bool: True if token is available, False otherwise
        """
        return bool(self.token_store and self.token_store.get("access_token"))

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

    def create_in_ditto(self, payload, toe_id, payload_type, create_parent: bool = True):
        """
        Creates a thing in Ditto and optionally updates the parent thing.
        
        Args:
            payload: Thing payload
            toe_id: Target of Evaluation ID
            payload_type: Type of payload
            create_parent: Whether to create/update parent thing (default: True)
        """

        # Check if thing already exists using pattern-based search
        existing_thing_id = self.search_item(toe_id, payload_type)
        if existing_thing_id is not None:
            logger.warning(f"Thing with toe_id={toe_id} and type={payload_type} already exists: {existing_thing_id}")
            
            # Parse the new payload to compare with existing
            payload_json = json.loads(payload)
            
            # Compare the existing thing with the new payload
            if self.compare_items(existing_thing_id, payload_json):
                logger.info(f"Thing content is identical, no update needed")
                return {
                    "success": False,
                    "error": "Thing already exists with identical content",
                    "thing_id": existing_thing_id,
                    "message": "Thing already exists and content is identical"
                }
            else:
                # Content differs - AUTO-UPDATE the existing thing
                logger.info(f"Thing exists but content differs, automatically updating")
                
                # Add thingId to payload for update
                payload_json["thingId"] = existing_thing_id
                
                # Call update_item to update the existing thing
                update_result = self.update_item(toe_id, payload_type, payload_json)
                
                if update_result.get("success"):
                    # Update parent thing
                    if create_parent:
                        self.update_parent_thing(toe_id, existing_thing_id, payload_type, operation="update")
                    
                    return {
                        "success": True,
                        "status_code": update_result.get("status_code"),
                        "thing_id": existing_thing_id,
                        "message": "Thing updated successfully with new content",
                        "action": "updated"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to update thing",
                        "thing_id": existing_thing_id,
                        "details": update_result.get("error")
                    }

        # Generate new unique ID only after confirming thing doesn't exist
        ctrl_id = self.name_thiing_id(toe_id, payload_type)

        payload_json = json.loads(payload)
        payload_json["thingId"] = ctrl_id

        logger.info(f"Controller attaching thing ID: {payload_json['thingId']}")
        logger.info("Creating policy in Ditto")

        policy_result = self.create_policy()
        if policy_result is None:
            logger.error("Failed to create policy")
            return {
                "success": False,
                "error": "Failed to create policy in Ditto"
            }
        
        policy_response, policy_name = policy_result
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

            result = {
                "success": 200 <= r.status_code < 300,
                "status_code": r.status_code,
                "response": response_data,
                "thing_id": thing_id,
                "action": "created"
            }
            
# Create/Update parent thing
            if create_parent and result["success"]:
                # Ensure parent thing exists
                parent_result = self.create_parent_thing(toe_id)

                # Add child thing to parent
                self.update_parent_thing(toe_id, thing_id, payload_type, operation="add")

                result["parent_thing_id"] = self.get_parent_thing_id(toe_id)
            
            return result
            
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

    def read_item(self, toe_id, category):
        """
        Reads a thing from Ditto by toe_id and category.
        
        Args:
            toe_id (str): Target of Evaluation ID
            category (str): Category (e.g., 'AI', 'BOMS')
        
        Returns:
            dict or None: Thing data if found, None otherwise
        """
        logger.info(f"Reading thing for toe_id: {toe_id}, category: {category}")
        
        # Search for the Thing ID
        item_id = self.search_item(toe_id, category)
        if not item_id:
            logger.error(f"Thing not found for toe_id {toe_id} and category {category}")
            return None
        
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

    def read_item_by_id(self, item_id):
        """
        Reads a thing from Ditto by its full thing ID.
        
        Args:
            item_id (str): Full Thing ID
        
        Returns:
            dict or None: Thing data if found, None otherwise
        """
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

    def search_file_by_name(self, toe_id: str, category: str, filename: str):
        """
        Search for a FILE type thing by toe_id, category, and specific filename.
        This prevents different files from overwriting each other.
        
        Args:
            toe_id: Target of Evaluation ID
            category: Category (FILE)
            filename: Exact filename to search for
            
        Returns:
            str: Thing ID if found with matching filename, None otherwise
        """
        logger.info(f"Searching for FILE by filename: toe_id={toe_id}, category={category}, filename={filename}")
        
        namespace = "cobalt.sdt"
        item_pattern = f"{namespace}:toe-{toe_id}-{category}"
        
        # Get all FILE things for this TOE
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/search/things?filter=like(thingId,"{item_pattern}*")&fields=thingId,attributes'
        
        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            logger.info(f"Sending GET request to {url}")
            r = session.get(url, headers={'accept': 'application/json'})
            
            if r.status_code == 200:
                response_json = r.json()
                items = response_json.get("items", [])
                
                logger.info(f"Found {len(items)} FILE things, checking filenames...")
                
                # Check each item's filename attribute
                for item in items:
                    item_filename = item.get("attributes", {}).get("filename")
                    thing_id = item.get("thingId")
                    
                    logger.info(f"  Checking {thing_id}: filename='{item_filename}'")
                    
                    if item_filename == filename:
                        logger.info(f"✅ Found matching file: {thing_id}")
                        return thing_id
                
                logger.info(f"❌ No FILE thing found with filename: {filename}")
                return None
            else:
                logger.error(f"Error searching files: Status code {r.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for file by name: {e}")
            return None

    def delete_item(self, toe_id, level, update_parent: bool = True):
        """
        Deletes a thing and updates the parent thing.
        
        Args:
            toe_id: Target of Evaluation ID
            level: Thing type/level
            update_parent: Whether to update parent thing
        """

        # First search for the existing thing ID
        item_id = self.search_item(toe_id, level)
        
        if not item_id:
            logger.error(f"Thing with toe_id {toe_id} and level {level} does not exist and cannot be deleted")
            return {"success": False, "error": "Thing does not exist"}
        
        logger.info(f"Attempting to delete thing with ID: {item_id}")

        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{item_id}'

        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.delete(url)

            # Check if response is successful (2xx status code)
            if 200 <= r.status_code < 300:
                # Verify deletion by checking if the thing still exists
                verification = self.read_item_by_id(item_id)
                if verification is None:
                    logger.info(f"Thing with ID {item_id} was successfully deleted")
                    
                    # Update parent thing
                    if update_parent:
                        self.update_parent_thing(toe_id, item_id, level, operation="delete")
                    
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
            return {"success": False, "error": str(e)}

    def update_item(self, toe_id, category, payload):
        """
        Updates a thing in Ditto after validating existence and content.
        
        Args:
            toe_id (str): Target of Evaluation ID
            category (str): Category (e.g., 'AI', 'BOMS')
            payload (dict or str): Updated payload
        
        Returns:
            dict: Update result
        """
        logger.info(f"Updating thing for toe_id: {toe_id}, category: {category}")
        
        # Step 1: Search for existing Thing ID
        item_id = self.search_item(toe_id, category)
        if not item_id:
            logger.error(f"Thing not found for toe_id {toe_id} and category {category}")
            return {"success": False, "error": "Thing not found"}
        
        # Step 2: Read existing Thing for full content validation
        existing_thing = self.read_item_by_id(item_id)
        if not existing_thing:
            return {"success": False, "error": "Failed to read existing thing"}
        
        try:
            # Step 3: Parse and validate payload
            payload_json = payload if isinstance(payload, dict) else json.loads(payload)
            
            # Step 4: Merge payload with existing Thing (full content check)
            updated_thing = existing_thing.copy()
            updated_thing.update(payload_json)  # Merge attributes/features
            updated_thing["thingId"] = item_id  # Ensure correct ID
            
            # Step 5: Create/update policy
            policy_response, policy_name = self.create_policy()
            updated_thing["policyId"] = policy_name
            
            # Step 6: Send update to Ditto
            url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{item_id}'
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=updated_thing, headers={'Content-Type': 'application/json'})
            
            response_data = r.json() if r.text else {}
            logger.info(f"Ditto update response status: {r.status_code}")
            
            # Step 7: Update parent thing
            self.update_parent_thing(toe_id, item_id, category, operation="update")
            
            return {
                "success": 200 <= r.status_code < 300,
                "status_code": r.status_code,
                "response": response_data,
                "thing_id": item_id
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
        Compares two items based on their source type and appropriate identifiers.
        
        Args:
            item_id1 (str): The ID of the first item in Ditto
            payload2 (dict or str): The new payload to compare
            
        Returns:
            bool: True if items are equal, False otherwise
        """
        logger.info(f"Comparing item {item_id1} with new payload")
        
        # Get existing thing from Ditto
        payload1 = self.read_item_by_id(item_id1)
        if payload1 is None:
            logger.error(f"Could not read item {item_id1}")
            return False
        
        # Convert payload2 to dict if string
        if isinstance(payload2, str):
            payload2 = json.loads(payload2)
        
        # Determine source type
        source_type = payload1.get("attributes", {}).get("sourceType") or payload2.get("attributes", {}).get("sourceType")
        
        logger.info(f"Comparing items of type: {source_type}")
        
        # Compare based on source type
        if source_type == "cyclonedx":
            return self._compare_cyclonedx(payload1, payload2)
        elif source_type == "oscal-component":
            return self._compare_oscal(payload1, payload2)
        elif source_type == "arm-template":
            return self._compare_arm(payload1, payload2)
        elif source_type == "extracted_file":
            return self._compare_extracted_file(payload1, payload2)
        elif source_type == "Repository":
            return self._compare_by_last_commit(payload1, payload2)
        else:
            logger.warning(f"Unknown source type: {source_type}, falling back to basic comparison")
            return self._compare_basic(payload1, payload2)

    def _compare_cyclonedx(self, payload1, payload2):
        """Compare CycloneDX BOMs comprehensively including deployment details."""
        # Check basic metadata
        print (payload1)
        print("--------------------")
        print (payload2)
        serial1 = payload1.get("attributes", {}).get("serialNumber")
        serial2 = payload2.get("attributes", {}).get("serialNumber")

        if serial1 != serial2:
            logger.info(f"CycloneDX serialNumber differs: {serial1} vs {serial2}")
            return False

        # Check BOM version
        version1 = payload1.get("attributes", {}).get("version")
        version2 = payload2.get("attributes", {}).get("version")

        if version1 != version2:
            logger.info(f"CycloneDX version differs: {version1} vs {version2}")
            return False

        # Check spec version
        spec1 = payload1.get("attributes", {}).get("specVersion")
        spec2 = payload2.get("attributes", {}).get("specVersion")

        if spec1 != spec2:
            logger.info(f"CycloneDX specVersion differs: {spec1} vs {spec2}")
            return False

        # Compare components count
        components1 = payload1.get("features", {}).get("components", {}).get("properties", {})
        components2 = payload2.get("features", {}).get("components", {}).get("properties", {})

        if len(components1) != len(components2):
            logger.info(f"CycloneDX component count differs: {len(components1)} vs {len(components2)}")
            return False

        # Hash the entire components section
        hash1 = hashlib.sha256(json.dumps(components1, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.sha256(json.dumps(components2, sort_keys=True).encode()).hexdigest()

        if hash1 != hash2:
            logger.info(f"CycloneDX components content differs (hash mismatch)")
            return False

        # Compare vulnerabilities count
        vuln1 = payload1.get("features", {}).get("vulnerabilities", {}).get("properties", {})
        vuln2 = payload2.get("features", {}).get("vulnerabilities", {}).get("properties", {})

        if len(vuln1) != len(vuln2):
            logger.info(f"CycloneDX vulnerability count differs: {len(vuln1)} vs {len(vuln2)}")
            return False

        # Hash the entire vulnerabilities section
        vuln_hash1 = hashlib.sha256(json.dumps(vuln1, sort_keys=True).encode()).hexdigest()
        vuln_hash2 = hashlib.sha256(json.dumps(vuln2, sort_keys=True).encode()).hexdigest()

        if vuln_hash1 != vuln_hash2:
            logger.info(f"CycloneDX vulnerabilities content differs (hash mismatch)")
            return False

        # Compare x-services
        services1 = payload1.get("features", {}).get("x-services", {}).get("properties", [])
        services2 = payload2.get("features", {}).get("x-services", {}).get("properties", [])

        if services1 != services2:
            logger.info(f"CycloneDX x-services differ")
            return False

        logger.info("CycloneDX BOMs are identical")
        return True

    def _compare_oscal(self, payload1, payload2):
        """Compare OSCAL components comprehensively including deployment details."""
        # Check basic metadata
        metadata1 = payload1.get("features", {}).get("metadata", {}).get("properties", {})
        metadata2 = payload2.get("features", {}).get("metadata", {}).get("properties", {})

        uuid1 = metadata1.get("uuid")
        uuid2 = metadata2.get("uuid")

        if uuid1 != uuid2:
            logger.info(f"OSCAL UUID differs: {uuid1} vs {uuid2}")
            return False

        # Check version
        version1 = metadata1.get("version")
        version2 = metadata2.get("version")

        if version1 != version2:
            logger.info(f"OSCAL version differs: {version1} vs {version2}")
            return False

        # Compare components count
        components1 = payload1.get("features", {}).get("components", {}).get("properties", [])
        components2 = payload2.get("features", {}).get("components", {}).get("properties", [])

        if len(components1) != len(components2):
            logger.info(f"OSCAL component count differs: {len(components1)} vs {len(components2)}")
            return False

        # Hash the entire components section
        hash1 = hashlib.sha256(json.dumps(components1, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.sha256(json.dumps(components2, sort_keys=True).encode()).hexdigest()

        if hash1 != hash2:
            logger.info(f"OSCAL components content differs (hash mismatch)")
            return False

        logger.info("OSCAL components are identical")
        return True

    def _compare_arm(self, payload1, payload2):
        """Compare ARM templates using content hash."""
       
        
        # Get schema and contentVersion
        schema1 = payload1.get("attributes", {}).get("$schema")
        schema2 = payload2.get("attributes", {}).get("$schema")
        
        if schema1 != schema2:
            logger.info(f"ARM schema differs: {schema1} vs {schema2}")
            return False
        
        version1 = payload1.get("attributes", {}).get("contentVersion")
        version2 = payload2.get("attributes", {}).get("contentVersion")
        
        if version1 != version2:
            logger.info(f"ARM contentVersion differs: {version1} vs {version2}")
            return False
        
        # Compare resource count
        resources1 = payload1.get("features", {}).get("resources", {}).get("properties", {})
        resources2 = payload2.get("features", {}).get("resources", {}).get("properties", {})
        
        if len(resources1) != len(resources2):
            logger.info(f"ARM resource count differs: {len(resources1)} vs {len(resources2)}")
            return False
        
        # Deep compare: hash the entire resources section
        hash1 = hashlib.sha256(json.dumps(resources1, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.sha256(json.dumps(resources2, sort_keys=True).encode()).hexdigest()
        
        if hash1 != hash2:
            logger.info(f"ARM resources content differs (hash mismatch)")
            return False
        
        logger.info("ARM templates are identical")
        return True

    def _compare_by_last_commit(self, payload1, payload2):
        """Fallback comparison using Git last_commit (for repositories)."""
        item1_last_modified = payload1.get("features", {}).get("repository", {}).get("properties", {}).get("last_commit", {})
        item2_last_modified = payload2.get("features", {}).get("repository", {}).get("properties", {}).get("last_commit", {})
        
        if item1_last_modified == item2_last_modified:
            logger.info("Items have same last_commit")
            return True
        else:
            logger.info("Items have different last_commit")
            return False

    def _compare_extracted_file(self, payload1, payload2):
        """
        Compare extracted files from IDS connector using file metadata.
        For FILE category things with uploaded/extracted files.
        """
        logger.info("Comparing extracted files")
        
        # ✅ PRIORITY 1: Compare filenames first (most specific identifier)
        filename1 = payload1.get("attributes", {}).get("filename")
        filename2 = payload2.get("attributes", {}).get("filename")
        
        if filename1 and filename2 and filename1 != filename2:
            logger.info(f"Extracted files differ by filename: '{filename1}' vs '{filename2}'")
            return False
        
        logger.info(f"Comparing files with same filename: {filename1}")
        
        # ✅ PRIORITY 2: Compare file size (quick check)
        size1 = payload1.get("features", {}).get("file_metadata", {}).get("properties", {}).get("size")
        size2 = payload2.get("features", {}).get("file_metadata", {}).get("properties", {}).get("size")
        
        if size1 != size2:
            logger.info(f"Extracted files differ by size: {size1} bytes vs {size2} bytes")
            return False
        
        logger.info(f"Files have same size: {size1} bytes")
        
        # ✅ PRIORITY 3: Compare file type/format
        type1 = payload1.get("features", {}).get("file_metadata", {}).get("properties", {}).get("type")
        type2 = payload2.get("features", {}).get("file_metadata", {}).get("properties", {}).get("type")
        
        if type1 != type2:
            logger.info(f"Extracted files differ by type: '{type1}' vs '{type2}'")
            return False
        
        logger.info(f"Files have same type: {type1}")
        
        # ✅ PRIORITY 4: Compare file hash if both files exist on disk (most reliable for content)
        file_path1 = payload1.get("attributes", {}).get("file_path")
        file_path2 = payload2.get("attributes", {}).get("file_path")
        
        if file_path1 and file_path2 and os.path.exists(file_path1) and os.path.exists(file_path2):
            try:
                hash1 = self.trs.get_file_hash(file_path1)
                hash2 = self.trs.get_file_hash(file_path2)
                
                logger.info(f"File hash comparison: hash1={hash1[:16]}..., hash2={hash2[:16]}...")
                
                if hash1 != hash2:
                    logger.info(f"Extracted files differ by content hash - FILES ARE DIFFERENT")
                    return False
                
                logger.info(f"Files have identical content (hash match)")
            except Exception as e:
                logger.warning(f"Could not compare file hashes: {e}")
        
        # ✅ PRIORITY 5: Compare updated timestamp (detects re-uploads of same file)
        updated1 = payload1.get("features", {}).get("timestamps", {}).get("properties", {}).get("updated")
        updated2 = payload2.get("features", {}).get("timestamps", {}).get("properties", {}).get("updated")
        
        if updated1 != updated2:
            logger.info(f"Extracted files differ by update time: {updated1} vs {updated2}")
            return False
        
        logger.info(f"Files have same update timestamp: {updated1}")
        
        # ✅ PRIORITY 6: Compare resource_id (IDS resource identifier)
        resource_id1 = payload1.get("attributes", {}).get("resource_id")
        resource_id2 = payload2.get("attributes", {}).get("resource_id")
        
        if resource_id1 and resource_id2 and resource_id1 != resource_id2:
            logger.info(f"Extracted files differ by resource_id: {resource_id1} vs {resource_id2}")
            return False
        
        logger.info("✅ Extracted files are IDENTICAL - all checks passed")
        return True

    def _compare_basic(self, payload1, payload2):
        """
        Basic fallback comparison for unknown types.
        Compares key attributes only.
        """
        logger.info("Using basic comparison (attributes only)")
        
        # Compare key attributes
        attrs1 = payload1.get("attributes", {})
        attrs2 = payload2.get("attributes", {})
        
        # Compare critical fields
        critical_fields = ["toe_id", "category", "sourceType", "updated", "transformedAt"]
        
        for field in critical_fields:
            val1 = attrs1.get(field)
            val2 = attrs2.get(field)
            
            if val1 != val2:
                logger.info(f"Items differ in {field}: {val1} vs {val2}")
                return False
        
        logger.info("Items appear identical (basic comparison)")
        return True

    # ======================= Parent Thing Methods =======================

    def create_parent_thing(self, toe_id: str, metadata: dict = None):
        """
        Creates a parent thing for a TOE ID that tracks all related things.
        
        Args:
            toe_id (str): Target of Evaluation ID
            metadata (dict): Optional metadata about the TOE
            
        Returns:
            dict: Result of parent thing creation
        """
        logger.info(f"Creating parent thing for TOE ID: {toe_id}")
        
        # Check if parent thing already exists
        parent_id = self.get_parent_thing_id(toe_id)
        existing_parent = self.read_item_by_id(parent_id)
        
        if existing_parent:
            logger.info(f"Parent thing already exists: {parent_id}")
            return {
                "success": True,
                "thing_id": parent_id,
                "message": "Parent thing already exists",
                "action": "exists"
            }
        
        # Create parent thing payload
        parent_payload = {
            "thingId": parent_id,
            "attributes": {
                "toe_id": toe_id,
                "type": "parent",
                "description": metadata.get("description", f"Parent thing for TOE {toe_id}") if metadata else f"Parent thing for TOE {toe_id}",
                "created_at": datetime.now().isoformat(),
                "owner": metadata.get("owner", "unknown") if metadata else "unknown",
                "project": metadata.get("project", "unknown") if metadata else "unknown",
                "metadata": metadata or {}
            },
            "features": {
                "child_things": {
                    "properties": {}
                },
                "statistics": {
                    "properties": {
                        "total_things": 0,
                        "things_by_type": {},
                        "last_updated": datetime.now().isoformat()
                    }
                }
            }
        }
        
        # Create policy and attach
        policy_response, policy_name = self.create_policy()
        parent_payload["policyId"] = policy_name
        
        # Create the parent thing in Ditto
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{parent_id}'
        
        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=parent_payload, headers={'Content-Type': 'application/json'})
            
            response_data = r.json() if r.text else {}
            logger.info(f"Parent thing created with status: {r.status_code}")
            
            return {
                "success": 200 <= r.status_code < 300,
                "status_code": r.status_code,
                "thing_id": parent_id,
                "response": response_data,
                "action": "created"
            }
        except Exception as e:
            logger.error(f"Error creating parent thing: {e}")
            return {"success": False, "error": str(e)}

    def get_parent_thing_id(self, toe_id: str):
        """
        Generates the parent thing ID for a TOE ID.
        
        Args:
            toe_id (str): Target of Evaluation ID
            
        Returns:
            str: Parent thing ID
        """
        namespace = "cobalt.sdt"
        return f"{namespace}:parent-{toe_id}"

    def update_parent_thing(self, toe_id: str, child_thing_id: str, payload_type: str, operation: str = "add"):
        """
        Updates the parent thing when child things are added/updated/deleted.
        
        Args:
            toe_id (str): Target of Evaluation ID
            child_thing_id (str): ID of the child thing
            payload_type (str): Type of the child thing (AI, QDT, BOMS, etc.)
            operation (str): Operation type - "add", "update", or "delete"
            
        Returns:
            dict: Result of parent thing update
        """
        logger.info(f"Updating parent thing for TOE {toe_id}, operation: {operation}")
        
        parent_id = self.get_parent_thing_id(toe_id)
        parent_thing = self.read_item_by_id(parent_id)
        
        if not parent_thing:
            logger.error(f"Parent thing not found: {parent_id}")
            return {"success": False, "error": "Parent thing not found"}
        
        # Get current child things
        child_things = parent_thing.get("features", {}).get("child_things", {}).get("properties", {})
        statistics = parent_thing.get("features", {}).get("statistics", {}).get("properties", {})
        things_by_type = statistics.get("things_by_type", {})
        
        # Perform operation
        if operation == "add" or operation == "update":
            # Read the child thing to get its details
            child_thing = self.read_item_by_id(child_thing_id)
            
            if child_thing:
                child_things[child_thing_id] = {
                    "thing_id": child_thing_id,
                    "type": payload_type,
                    "created_at": child_thing.get("attributes", {}).get("transformedAt") or datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "attributes": {
                        "sourceType": child_thing.get("attributes", {}).get("sourceType"),
                        "componentName": child_thing.get("attributes", {}).get("componentName"),
                        "componentVersion": child_thing.get("attributes", {}).get("componentVersion")
                    }
                }
                
                # Update statistics
                things_by_type[payload_type] = things_by_type.get(payload_type, 0) + (1 if operation == "add" else 0)
                
        elif operation == "delete":
            if child_thing_id in child_things:
                removed_type = child_things[child_thing_id].get("type")
                del child_things[child_thing_id]
                
                # Update statistics
                if removed_type in things_by_type:
                    things_by_type[removed_type] = max(0, things_by_type[removed_type] - 1)
        
        # Update statistics
        statistics["total_things"] = len(child_things)
        statistics["things_by_type"] = things_by_type
        statistics["last_updated"] = datetime.now().isoformat()
        
        # Update parent thing
        parent_thing["features"]["child_things"]["properties"] = child_things
        parent_thing["features"]["statistics"]["properties"] = statistics
        
        # Send update to Ditto
        url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{parent_id}'
        try:
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            r = session.put(url, json=parent_thing, headers={'Content-Type': 'application/json'})
            
            response_data = r.json() if r.text else {}
            logger.info(f"Parent thing updated with status: {r.status_code}")
            
            return {
                "success": 200 <= r.status_code < 300,
                "status_code": r.status_code,
                "thing_id": parent_id,
                "response": response_data
            }
        except Exception as e:
            logger.error(f"Error updating parent thing: {e}")
            return {"success": False, "error": str(e)}

    def get_parent_thing(self, toe_id: str):
        """
        Retrieves the parent thing for a TOE ID.
        
        Args:
            toe_id (str): Target of Evaluation ID (can be plain UUID or full parent thing ID)
            
        Returns:
            dict: Parent thing or None
        """
        # If toe_id already contains the parent prefix, use it directly
        if toe_id.startswith("cobalt.sdt:parent-"):
            parent_id = toe_id
        else:
            # Otherwise, construct the parent ID
            parent_id = self.get_parent_thing_id(toe_id)
        
        return self.read_item_by_id(parent_id)

    def list_child_things(self, toe_id: str):
        """
        Lists all child things under a parent thing.
        
        Args:
            toe_id (str): Target of Evaluation ID
            
        Returns:
            dict: List of child things
        """
        parent_thing = self.get_parent_thing(toe_id)
        
        if not parent_thing:
            return {"success": False, "error": "Parent thing not found"}
        
        child_things = parent_thing.get("features", {}).get("child_things", {}).get("properties", {})
        statistics = parent_thing.get("features", {}).get("statistics", {}).get("properties", {})
        
        return {
            "success": True,
            "toe_id": toe_id,
            "parent_thing_id": self.get_parent_thing_id(toe_id),
            "total_things": statistics.get("total_things", 0),
            "things_by_type": statistics.get("things_by_type", {}),
            "child_things": child_things,
            "last_updated": statistics.get("last_updated")
        }

        
        if item1_last_modified == item2_last_modified:
            logger.info("Items have same last_commit")
            return True
        else:
            logger.info("Items have different last_commit")
            return False


# ===========================================Evidence Provider methods===========================================
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

        thing_with_repo = self.read_item_by_id(thing_id)
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

# changed on 10th Oct 2023 to MQTT
    # def listen_to_ditto(self):
        

    #     def on_connect(client, userdata, flags, rc):
    #         print("Connected to MQTT broker with result code", rc)
    #         client.subscribe("ditto-cobalt/#")

    #     def on_message(client, userdata, msg):
    #         print("*************************************Ditto MQTT Listener*******************************")
    #         print(f"Topic: {msg.topic}")
    #         try:
    #             payload = msg.payload.decode()
    #             print("Raw MQTT message:", payload)
    #             outputJS = json.loads(payload)

    #             # Check if this is a deletion event by inspecting the topic
    #             topic = outputJS.get('topic', '')
    #             if '/events/deleted' in topic:
    #                 print("Deletion event detected - ignoring")
    #                 return

    #             thing = outputJS.get('value', {})
    #             thing_id = thing.get('thingId')
    #             attributes = thing.get('attributes', {})
    #             toe_id = attributes.get('toe_id')
    #             level = attributes.get('category')
    #             print(f"thing_id: {thing_id}, toe_id: {toe_id}, level: {level}")
    #             self.get_evidence(toe_id=toe_id, level=level, thing_id=thing_id, notify=True)
    #         except Exception as e:
    #             print("Error parsing MQTT message:", e)

    #     client = mqtt.Client()
    #     client.on_connect = on_connect
    #     client.on_message = on_message
    #     client.connect("localhost", 1883, 60)
    #     client.loop_forever()
    def listen_to_ditto(self):
        """
        Enhanced MQTT listener that routes to configured evidence collectors
        """
        
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

                # Check if this is a deletion event
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
                
                # NEW: Route to configured evidence collectors based on template
                matching_collectors = self.ep.get_subscribed_collectors(msg.topic, thing)
                
                if matching_collectors:
                    print(f"Found {len(matching_collectors)} matching collectors")
                    for collector in matching_collectors:
                        collector_id = collector.get("collector_id")
                        print(f"Notifying collector: {collector_id}")
                        
                        try:
                            self.ep.send_notification(collector, thing)
                        except Exception as e:
                            logger.error(f"Error notifying {collector_id}: {e}")
                else:
                    # Fallback to old method for backward compatibility
                    print("No matching collectors, using legacy notification")
                    self.get_evidence(toe_id=toe_id, level=level, thing_id=thing_id, notify=True)
                    
            except Exception as e:
                print("Error parsing MQTT message:", e)
                import traceback
                traceback.print_exc()

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect("localhost", 1883, 60)
        client.loop_forever()


    def run_ditto_listener(self):
        """It starts a new thread invoking method run_default()

        """
        try:
            start_new_thread(self.listen_to_ditto, ())
        except Exception as e:
            print("ERROR:{}".format(e))

#==========================OLD Demo Github sync Methods==========================

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
                    response = self.update_item(toe_id, level, repo_path_thing)
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

#==========================IDS Connector Methods==========================

    # OLD METHODS - COMMENTED OUT
    # def sync_ids_connector(self, data_source_url: str, toe_id: str, category: str):
    #     """
    #     Handles IDS connector communication and data fetching
    #     """
    #     logger.info(f"Controller: Initiating IDS connector sync from {data_source_url}")
    #     
    #     try:
    #         # Make HTTP call to IDS connector
    #         
    #         response = requests.post(
    #             "http://true-connector:8080/api/data/fetch",
    #             json={
    #                 "source_url": data_source_url,
    #                 "callback_url": f"http://your-sdt-api:8000/api/SDT/receive",
    #                 "toeid": toe_id,
    #                 "category": category
    #             },
    #             timeout=30
    #         )
    #         response.raise_for_status()
    #         
    #         logger.info("IDS connector fetch initiated successfully")
    #         return {"message": "Data fetch initiated", "status": "pending"}
    #         
    #     except Exception as e:
    #         logger.error(f"Error in IDS connector sync: {e}")
    #         raise Exception(f"IDS connector sync failed: {str(e)}")

    # def receive_and_process_file(self, file_content: bytes, filename: str, toe_id: str, category: str, metadata: str = "{}"):
    #     """
    #     Processes received files and creates digital twin
    #     """
    #     logger.info(f"Controller: Processing received file {filename}")
    #     
    #     try:
    #         import os
    #         # Create evidence directory if it doesn't exist
    #         os.makedirs("evidence", exist_ok=True)
    #         
    #         # Save the file
    #         file_path = f"evidence/{toe_id}_{category}_{filename}"
    #         with open(file_path, "wb") as f:
    #             f.write(file_content)
    #         
    #         # Forward to translator for processing
    #         result = self.trs.process_received_file(file_path, filename, toe_id, category, metadata)
    #         
    #         # Create digital twin in Ditto
    #         self.create_in_ditto(result, toe_id, category)
    #         
    #         logger.info(f"File processed and digital twin created successfully")
    #         return {"message": "File processed and twin created", "file_path": file_path}
    #         
    #     except Exception as e:
    #         logger.error(f"Error processing received file: {e}")
    #         raise Exception(f"File processing failed: {str(e)}")

    # def register_webhook(self, provider_id: str, dataset_id: str, toe_id: str, category: str, webhook_url: str):
    #     """
    #     Registers webhook with external IDS connector
    #     """
    #     logger.info(f"Controller: Registering webhook for provider {provider_id}")
    #     
    #     try:
    #         webhook_payload = {
    #             "webhook_url": webhook_url,
    #             "provider_id": provider_id,
    #             "dataset_id": dataset_id,
    #             "filters": {"category": category, "file_types": [".h5", ".py", ".ipynb", ".txt"]}
    #         }
    #         
    #         response = requests.post(
    #             "http://ids-connector:8080/api/subscribe",
    #             json=webhook_payload,
    #             timeout=30
    #         )
    #         response.raise_for_status()
    #         
    #         logger.info("Webhook registration successful")
    #         return {"message": "Subscription created", "status": "active"}
    #         
    #     except Exception as e:
    #         logger.error(f"Error registering webhook: {e}")
    #         raise Exception(f"Webhook registration failed: {str(e)}")

    # def process_webhook(self, toe_id: str, payload: dict):
    #     """
    #     Processes webhook notifications and downloads files
    #     """
    #     logger.info(f"Controller: Processing webhook for TOE {toe_id}")
    #     
    #     try:
    #         # Extract file URL from webhook payload
    #         file_url = payload.get("file_url")
    #         category = payload.get("category", "AI")
    #         
    #         if not file_url:
    #             raise Exception("No file_url found in webhook payload")
    #         
    #         # Forward to translator to download and process file
    #         result = self.trs.download_and_process_file(file_url, toe_id, category)
    #         
    #         # Create digital twin in Ditto
    #         self.create_in_ditto(result["thing_data"], toe_id, category)
    #         
    #         logger.info("Webhook processed successfully")
    #         return {"message": "Webhook processed successfully", "file_path": result.get("file_path")}
    #         
    #     except Exception as e:
    #         logger.error(f"Error processing webhook: {e}")
    #         raise Exception(f"Webhook processing failed: {str(e)}")

    def sync_ids_connector(self, data_path: str, toe_id: str, ids_connector_url: str = "http://localhost:8004"):
        """
        Sync data from IDS connector using OAuth2 Bearer token authentication
        
        Args:
            data_path: Path to data in IDS connector ('all' or specific resource name)
            toe_id: Target of Evaluation ID
            ids_connector_url: Base URL of IDS connector
            
        Returns:
            dict: Result of sync operation
        """
        logger.info(f"Syncing from IDS connector: {ids_connector_url}, data_path: {data_path}")
        
        try:
            # Call IDS connector endpoint
            url = f"{ids_connector_url}/api/IDSconnector/get_data_request"
            params = {
                "data_path": data_path,
                "toe_id": toe_id,
                "data_type": "json"  # Default to json for now
            }
            
            # Get Bearer token authorization headers
            auth_headers = self.get_auth_headers()
            
            if not auth_headers:
                logger.warning("No Bearer token available — IDS-Connector authentication may fail")
                logger.info("Ensure SDT-Manager has distributed token via POST /auth/token")
            
            # Prepare headers for IDS-Connector request
            headers = {
                "Content-Type": "application/json",
                **auth_headers  # Include Bearer token if available
            }
            
            logger.info(f"Calling IDS connector: {url} with Bearer token auth")
            logger.debug(f"Authorization: {headers.get('Authorization', 'None')[:30] if headers.get('Authorization') else 'None'}")
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            ids_response = response.json()
            logger.info(f"Received IDS response: {ids_response.get('data_type')}")
            logger.info(f"Response data length: {len(ids_response.get('data', ''))}")
            
            # Process IDS response through translator
            processed_things = self.trs.process_ids_response(ids_response, toe_id)
            
            logger.info(f"Processed {len(processed_things)} things from IDS connector")
            
            # Create things in Ditto and update parent
            results = []
            for thing_json in processed_things:
                thing = json.loads(thing_json)
                category = thing.get("attributes", {}).get("category", "UNKNOWN")
                
                # ✅ For FILE types, check by filename first to prevent overwriting different files
                if category == "FILE":
                    filename = thing.get("attributes", {}).get("filename")
                    if filename:
                        existing_thing_id = self.search_file_by_name(toe_id, category, filename)
                        
                        if existing_thing_id:
                            # File with same name exists - compare and update if different
                            if self.compare_items(existing_thing_id, thing):
                                logger.info(f"File '{filename}' already exists with identical content, skipping")
                                results.append({
                                    "category": category,
                                    "filename": filename,
                                    "thing_id": existing_thing_id,
                                    "success": False,
                                    "action": "skipped",
                                    "message": "Identical file already exists"
                                })
                                continue
                            else:
                                # Same filename, different content - update
                                logger.info(f"File '{filename}' exists but content differs, updating")
                                update_result = self.update_item(toe_id, category, thing)
                                
                                if update_result.get("success"):
                                    self.update_parent_thing(toe_id, existing_thing_id, category, operation="update")
                                
                                results.append({
                                    "category": category,
                                    "filename": filename,
                                    "thing_id": existing_thing_id,
                                    "success": update_result.get("success"),
                                    "action": "updated"
                                })
                                continue
                        else:
                            # File doesn't exist - create new thing directly without search
                            logger.info(f"File '{filename}' not found, creating new Thing")
                            
                            # Generate new unique ID
                            ctrl_id = self.name_thiing_id(toe_id, category)
                            thing["thingId"] = ctrl_id
                            thing["policyId"] = "cobalt:policy"
                            thing["definition"] = "cobalt:evidence-file:1.0.0"
                            thing_json = json.dumps(thing)
                            
                            # Create policy
                            self.create_policy()
                            
                            # Create thing in Ditto directly (uses basic auth: ditto:ditto)
                            url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{ctrl_id}'
                            
                            session = requests.Session()
                            session.auth = ("ditto", "ditto")
                            
                            logger.info(f"Creating thing with ID: {ctrl_id}")
                            r = session.put(url, json=thing, headers={'Content-Type': 'application/json'})
                            logger.info(f"Ditto response status: {r.status_code}")
                            
                            if r.status_code in [201, 204]:
                                # Update parent thing
                                parent_result = self.create_parent_thing(toe_id)
                                self.update_parent_thing(toe_id, ctrl_id, category, operation="add")
                                
                                results.append({
                                    "category": category,
                                    "filename": filename,
                                    "thing_id": ctrl_id,
                                    "success": True,
                                    "action": "created"
                                })
                                continue
                            else:
                                results.append({
                                    "category": category,
                                    "filename": filename,
                                    "thing_id": ctrl_id,
                                    "success": False,
                                    "action": "failed",
                                    "error": r.text
                                })
                                continue
                
                # For non-FILE types, use standard create_in_ditto logic
                result = self.create_in_ditto(thing_json, toe_id, category, create_parent=True)
                
                results.append({
                    "category": category,
                    "filename": thing.get("attributes", {}).get("filename"),
                    "thing_id": result.get("thing_id"),
                    "success": result.get("success"),
                    "action": result.get("action")
                })
            
            # Update parent thing with IDS sync metadata
            self._update_parent_with_ids_sync(toe_id, data_path, len(processed_things))
            
            return {
                "success": True,
                "message": f"Synced {len(processed_things)} artifacts from IDS connector",
                "data_path": data_path,
                "results": results
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error(f"Unauthorized — Bearer token invalid or expired for IDS connector")
                logger.error(f"Please ensure SDT-Manager has distributed a valid token via POST /auth/token")
                return {
                    "success": False,
                    "error": "Unauthorized — Invalid or expired Bearer token",
                    "detail": "IDS-Connector rejected authentication. Make sure SDT-Manager has delivered a valid token.",
                    "status_code": 401
                }
            elif e.response.status_code == 403:
                logger.error(f"Forbidden — Bearer token lacks required permissions for IDS connector")
                return {
                    "success": False,
                    "error": "Forbidden — Bearer token lacks required permissions",
                    "detail": e.response.json() if e.response.text else str(e),
                    "status_code": 403
                }
            elif e.response.status_code == 404:
                logger.error(f"Resource not found in IDS connector: {data_path}")
                return {
                    "success": False,
                    "error": f"Resource not found: {data_path}",
                    "detail": e.response.json() if e.response.text else str(e)
                }
            else:
                logger.error(f"IDS connector HTTP error {e.response.status_code}: {e}")
                return {
                    "success": False,
                    "error": f"IDS connector error: HTTP {e.response.status_code}",
                    "detail": e.response.json() if e.response.text else str(e)
                }
        except Exception as e:
            logger.error(f"Error syncing from IDS connector: {e}")

            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }

    def _update_parent_with_ids_sync(self, toe_id: str, data_path: str, artifact_count: int):
        """
        Update parent thing with IDS sync metadata
        """
        
        
        try:
            parent_id = self.get_parent_thing_id(toe_id)
            parent_thing = self.read_item_by_id(parent_id)
            
            if not parent_thing:
                return
            
            # Add IDS sync history
            if "ids_sync_history" not in parent_thing.get("features", {}):
                parent_thing["features"]["ids_sync_history"] = {"properties": {}}
            
            sync_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            parent_thing["features"]["ids_sync_history"]["properties"][sync_id] = {
                "data_path": data_path,
                "artifact_count": artifact_count,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update parent
            url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{parent_id}'
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            session.put(url, json=parent_thing, headers={'Content-Type': 'application/json'})
            logger.info(f"Updated genesis thing with IDS sync metadata")
            
        except Exception as e:
            logger.error(f"Error updating genesis with IDS sync: {e}")


    # NEW GITHUB METHODS Similar to NEW IDS methods

    def sync_github_repository(self, github_url: str, toe_id: str, category: str):
        """
        Sync GitHub repository to Ditto instance and update parent thing
        
        Args:
            github_url: The URL of the GitHub repository to clone
            toe_id: Target of Evaluation ID
            category: Category/type of evidence (AI, BOMS, etc.)
            
        Returns:
            dict: Result of sync operation with repository details
        """
        logger.info(f"Syncing GitHub repository: {github_url} for TOE: {toe_id}, category: {category}")
        
        try:
            # Clone and process repository using translator
            repo_thing_json = self.trs.fetch_push_save_repo(toe_id, category, github_url)
            repo_thing = json.loads(repo_thing_json)
            
            # Extract repository name from URL
            repo_name = github_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            logger.info(f"Repository '{repo_name}' cloned and processed")
            
            # Check if repository thing already exists
            thing_id = self.search_item(toe_id, category)
            
            action = None
            if thing_id is not None:
                logger.info(f"Repository thing already exists: {thing_id}")
                
                # Compare existing thing with new one
                if self.compare_items(thing_id, repo_thing_json):
                    logger.info(f"Repository content unchanged, no update needed")
                    action = "unchanged"
                    result_thing_id = thing_id
                else:
                    logger.info(f"Repository content changed, updating thing")
                    update_result = self.update_item(toe_id, category, repo_thing)
                    action = "updated"
                    result_thing_id = thing_id
            else:
                # Create new thing in Ditto
                logger.info(f"Creating new repository thing in Ditto")
                create_result = self.create_in_ditto(repo_thing_json, toe_id, category, create_parent=True)
                action = "created"
                result_thing_id = create_result.get("thing_id")
            
            # Update parent thing with GitHub sync metadata
            self._update_parent_with_github_sync(toe_id, github_url, repo_name, category)
            
            return {
                "success": True,
                "message": f"GitHub repository '{repo_name}' {action} successfully",
                "repository_name": repo_name,
                "thing_id": result_thing_id,
                "action": action,
                "parent_updated": True
            }
            
        except Exception as e:
            logger.error(f"Error syncing GitHub repository: {e}")
            
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"Failed to sync GitHub repository: {str(e)}"
            }

    def _update_parent_with_github_sync(self, toe_id: str, github_url: str, repo_name: str, category: str):
        """
        Update parent thing with GitHub sync metadata
        """
        
        
        try:
            parent_id = self.get_parent_thing_id(toe_id)
            parent_thing = self.read_item_by_id(parent_id)
            
            if not parent_thing:
                logger.warning(f"Parent thing not found for TOE: {toe_id}")
                return
            
            # Add GitHub sync history feature if it doesn't exist
            if "github_sync_history" not in parent_thing.get("features", {}):
                parent_thing["features"]["github_sync_history"] = {"properties": {}}
            
            # Create unique sync ID with timestamp
            sync_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            parent_thing["features"]["github_sync_history"]["properties"][sync_id] = {
                "github_url": github_url,
                "repository_name": repo_name,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update parent thing
            url = f'http://{Ditto_IP}:{Ditto_PORT}/api/2/things/{parent_id}'
            session = requests.Session()
            session.auth = ("ditto", "ditto")
            session.put(url, json=parent_thing, headers={'Content-Type': 'application/json'})
            logger.info(f"Updated parent thing with GitHub sync metadata for repo: {repo_name}")
            
        except Exception as e:
            logger.error(f"Error updating parent with GitHub sync: {e}")
    
    def get_evidence_flexible(self, toe_id: str, category: str = None, 
                              evidence_type: str = "thing", files: list = None,
                              include_patterns: list = None, exclude_patterns: list = None,
                              format: str = "json", transform: str = None,
                              include_features: list = None, filename: str = None):
        """
        Flexible evidence retrieval with dynamic configuration.
        
        Args:
            toe_id: Target of Evaluation ID
            category: Category to filter (optional)
            evidence_type: Type of evidence (thing|zip|files|specific|auto)
            files: Specific files to retrieve (for files/specific type)
            include_patterns: Include patterns for ZIP (for zip type)
            exclude_patterns: Exclude patterns for ZIP (for zip type)
            format: Response format (json|download)
            transform: Transform name or custom mapping JSON
            include_features: Features to include (for thing type)
        
        Returns:
            Evidence data in requested format
        """
        logger.info(f"Flexible evidence retrieval: toe_id={toe_id}, type={evidence_type}, format={format}")
        
        try:
            # Get genesis thing
            genesis_id = self.get_genesis_thing_id(toe_id)
            genesis_thing = self.read_item_by_id(genesis_id)
            
            if not genesis_thing:
                logger.error(f"Genesis thing not found for TOE: {toe_id}")
                return {"error": "Genesis thing not found", "toe_id": toe_id}
            
            # Get thing IDs from correct feature structure
            child_things_feature = genesis_thing.get("features", {}).get("child_things", {})
            child_things_dict = child_things_feature.get("properties", {})
            
            # Extract thing IDs from child_things dictionary
            thing_ids = list(child_things_dict.keys())
            
            logger.info(f"Found {len(thing_ids)} things in parent for TOE {toe_id}")
            
            if not thing_ids:
                logger.warning(f"No child things found in parent for TOE: {toe_id}")
                return {
                    "error": "No things found in parent",
                    "toe_id": toe_id,
                    "hint": "Create things first using /api/SDT/create or /api/SDT/sync/github"
                }
            
            # Filter by category if specified
            if category:
                filtered_ids = []
                for thing_id, thing_info in child_things_dict.items():
                    if thing_info.get("type") == category:
                        filtered_ids.append(thing_id)
                
                if not filtered_ids:
                    logger.warning(f"No things found for category: {category}")
                    available_categories = list(set(t.get("type") for t in child_things_dict.values()))
                    return {
                        "error": f"No things found for category: {category}",
                        "toe_id": toe_id,
                        "available_categories": available_categories
                    }
                
                thing_ids = filtered_ids
            
            # Filter by filename if specified (for FILE category)
            if filename and category == "AI":
                filename_filtered = []
                for thing_id in thing_ids:
                    thing = self.read_item_by_id(thing_id)
                    if thing and thing.get("attributes", {}).get("filename") == filename:
                        filename_filtered.append(thing_id)
                
                if not filename_filtered:
                    logger.warning(f"No AI Artifacts found with filename: {filename}")
                    return {
                        "error": f"No AI Artifacts found with filename: {filename}",
                        "toe_id": toe_id,
                        "hint": "Check available filenames using format=json"
                    }
                
                thing_ids = filename_filtered
            
            # Get the first matching thing
            thing_id = thing_ids[0]
            thing = self.read_item_by_id(thing_id)
            if not thing:
                logger.error(f"Thing not found: {thing_ids[0]}")
                return {"error": "Thing not found", "thing_id": thing_ids[0]}
            
            # Build evidence configuration
            evidence_config = {
                "type": evidence_type,
                "files": files or [],
                "include": include_patterns or ["*"],
                "exclude": exclude_patterns or [],
                "include_features": include_features
            }
            
            # Prepare evidence using evidence provider
            evidence_data = self.ep.prepare_evidence_flexible(thing, evidence_config)
            
            # Apply transformation if specified
            if transform:
                evidence_data = self.ep.apply_transform_flexible(thing, evidence_data, transform)
                # When transform is applied, return only the transformed content
                return evidence_data
            
            # Return based on format
            if format == "json":
                return self._return_evidence_json(evidence_data, thing, evidence_type)
            elif format == "download":
                return self._return_evidence_download(evidence_data, thing, evidence_type)
            else:
                logger.warning(f"Unknown format: {format}, returning JSON")
                return self._return_evidence_json(evidence_data, thing, evidence_type)
        
        except Exception as e:
            logger.error(f"Error in flexible evidence retrieval: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "toe_id": toe_id}
    
    def _return_evidence_json(self, evidence_data: dict, thing: dict, evidence_type: str):
        """
        Return evidence as JSON metadata.
        """
        result = {
            "thing_id": thing.get("thingId"),
            "evidence_type": evidence_type,
            "timestamp": datetime.now().isoformat(),
            "data": evidence_data
        }
        
        # Add file metadata if files are present
        if evidence_type in ["files", "specific"] and isinstance(evidence_data, dict):
            files = evidence_data.get("files", [])
            result["files_count"] = len(files)
            result["files_metadata"] = [
                {"name": f.get("name"), "size": f.get("size"), "hash": f.get("hash")} 
                for f in files
            ]
        
        return result
    
    def _return_evidence_download(self, evidence_data: dict, thing: dict, evidence_type: str):
        """
        Return evidence as file download.
        This returns metadata that the API endpoint will use to construct FileResponse.
        """
        if evidence_type == "zip":
            # ZIP was created, return path for download
            if isinstance(evidence_data, dict) and "zip_path" in evidence_data:
                return {
                    "download": True,
                    "file_path": evidence_data["zip_path"],
                    "filename": f"{thing.get('thingId', 'evidence').replace(':', '_')}.zip",
                    "media_type": "application/zip"
                }
        
        elif evidence_type in ["files", "specific"]:
            # Create ZIP from specific files
            files_info = evidence_data.get("files", [])
            if files_info:
                zip_path = self._create_files_zip(files_info, thing.get("thingId"))
                return {
                    "download": True,
                    "file_path": zip_path,
                    "filename": f"{thing.get('thingId', 'evidence').replace(':', '_')}_files.zip",
                    "media_type": "application/zip"
                }
        
        elif evidence_type == "thing":
            # Convert thing to JSON file
            import tempfile
            temp_dir = tempfile.mkdtemp()
            thing_id = thing.get("thingId", "unknown").replace(":", "_")
            json_path = os.path.join(temp_dir, f"{thing_id}.json")
            
            with open(json_path, 'w') as f:
                json.dump(evidence_data, f, indent=2)
            
            return {
                "download": True,
                "file_path": json_path,
                "filename": f"{thing_id}.json",
                "media_type": "application/json"
            }
        
        # Fallback to JSON return
        return {
            "download": False,
            "error": "Cannot create download for this evidence type",
            "data": evidence_data
        }
    
    def _create_files_zip(self, files_info: list, thing_id: str):
        """
        Create a ZIP archive from list of files.
        """
        import tempfile
        import zipfile
        
        temp_dir = tempfile.mkdtemp()
        zip_filename = f"{thing_id.replace(':', '_')}_files.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in files_info:
                file_path = file_info.get("path")
                file_name = file_info.get("name")
                
                if file_path and os.path.exists(file_path):
                    zipf.write(file_path, file_name)
        
        logger.info(f"Created files ZIP with {len(files_info)} files at: {zip_path}")
        return zip_path
