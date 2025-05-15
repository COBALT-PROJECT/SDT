
import logging
import requests
from core.util import FileUtils
logger = logging.getLogger(__name__)
import os
import json
import uuid
from datetime import datetime
import json
import uuid
from datetime import datetime, timezone


Clouditor_IP = ""
Clouditor_PORT = ""

class EvidenceProvider():
    """
    EvidenceProvider class to handle evidence queries and notifications.
    This class is responsible for processing incoming queries and providing the necessary evidence
    based on the specified level.
    It also handles notifications.
    Attributes:
        controller (object): The controller instance to interact with.

    Methods:
        __init__(self, controller=None): 
            Initializes the EvidenceProvider instance.
        process_query(self, toe_id: str, level: str, json_data: dict): 
            Processes the incoming query and returns the evidence based on the specified level.
        notification_push(): 
            Handles notifications for evidence collectors.

    """


    def __init__(self, controller=None):
        print(f"SDT-EvidenceProvider instance created")
    
    def process_query(self, toe_id: str, level: str, json_data: dict):
        logger.info(f"Processing query for toe_id: {toe_id}, level: {level}")
    
        # print(json_data)
        # print("************")
        if level == "AI":
            # Get the evidence directory path from the controller for watch tower
            logger.info("Processing AI query")
        
            
            # print(repo_path)
            template = {
                "evidence_collector": "aishield",
                "evidence_type": "repository",
                "evidence_format": "zip",
                "evidence_categories": ["AI"],
            }
         
            logger.info(f"AI evidence template send")
            return template
        
        elif level == "BOMS":
            logger.info("Processing toe.BOMS query - not implemented")
            return
        elif level == "QDT":
            # Get the evidence directory path from the controller for clouditor
            logger.info("Processing QDT template")
        
            
            # print(repo_path)
            template = {
                "evidence_collector": "clouditor",
                "evidence_type": "paths",
                "file_name" : ["qpu_data.json"],
                "evidence_format": "file-by-file", # single  "file"
                "evidence_categories": ["QDT"],
            }
         
            logger.info(f"QDT evidence template send")
            return template
        
        elif level == "cloud":
            logger.info("Processing toe.cloud query - not implemented")
            return  
   

    def notification_push_AI(self, evidence_dir, toe_id):
        """
        Zips the evidence directory and sends it to a dummy AI endpoint.
        Uses FileUtils.zip_file from util.py
        """
        # Use the zip_file utility function instead of doing it manually
        zip_path, zip_filename = FileUtils.zip_file(evidence_dir, toe_id)
        
        dummy_url = "http://localhost:8002/upload/ai"  # Changed to localhost for testing
        
        with open(zip_path, "rb") as f:
            files = {"file": (zip_filename, f, "application/zip")}
            try:
                response = requests.post(dummy_url, files=files)
                logger.info(f"AI notification sent, status: {response.status_code}")
                # Clean up the temp file
                os.remove(zip_path)
                return response.status_code
            except Exception as e:
                logger.error(f"Failed to send AI notification: {e}")
                # Clean up the temp file even if there's an error
                os.remove(zip_path)
                return None
            
    # def notification_push_QDT(self, file_path, toe_id=None, filename=None, media_type="application/json"):
    #     """
    #     Reads a QPU data JSON file, transforms it to the required format, and sends it to the QDT endpoint.
    #     """

    #     dummy_url = f"http://10.160.101.141:8080/v1/assessment/evidences"
        
    #     # Read the JSON file
    #     try:
    #         with open(file_path, "r") as f:
    #             qpu_data = json.load(f)
            
    #         # Transform data
    #         transformed_data = self._transform_qpu_data(qpu_data, toe_id)
            
    #         # Send the transformed data
    #         try:
    #             response = requests.post(
    #                 dummy_url, 
    #                 json=transformed_data,
    #                 headers={"Content-Type": "application/json"}
    #             )
    #             logger.info(f"QDT notification sent, status: {response.status_code}")
    #             return response.status_code
    #         except Exception as e:
    #             logger.error(f"Failed to send QDT notification: {e}")
    #             return None
                
    #     except Exception as e:
    #         logger.error(f"Failed to process QPU data file: {e}")
    #         return None
    def notification_push_QDT(self, file_path, toe_id=None, filename=None, media_type="application/json"):
        """
        Reads a QPU data JSON file, transforms it to the required format, obtains an access token,
        and sends it to the QDT endpoint.
        """
        import requests
        import base64

        # Step 1: Get access token
        token_url = "http://10.160.101.137:8080/v1/auth/token"
        client_id = "clouditor"
        client_secret = "clouditor"
        basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}

        logger.info(f"Token request URL: {token_url}")
        logger.info(f"Token request headers: {headers}")
        logger.info(f"Token request data: {data}")

        try:
            token_resp = requests.post(token_url, headers=headers, data=data)
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")
            if not access_token:
                logger.error("No access token received from QDT auth endpoint.")
                return None
        except Exception as e:
            logger.error(f"Failed to obtain access token: {e}")
            return None

        # Step 2: Read and transform QPU data
        try:
            with open(file_path, "r") as f:
                qpu_data = json.load(f)
            transformed_data = self._transform_qpu_data(qpu_data, toe_id)
        except Exception as e:
            logger.error(f"Failed to process QPU data file: {e}")
            return None
        
        # Step 3: Send evidence to QDT endpoint
        evidence_url = "http://10.160.101.137:8080/v1/assessment/evidences"
        evidence_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Evidence request URL: {evidence_url}")
        logger.info(f"Evidence request headers: {evidence_headers}")
        logger.info(f"Evidence request payload: {json.dumps(transformed_data, indent=2)}")
        
        try:
            response = requests.post(
                evidence_url,
                headers=evidence_headers,
                json=transformed_data
            )
            logger.info(f"QDT notification sent, status: {response.status_code}")
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            return response.status_code
        except Exception as e:
            logger.error(f"Failed to send QDT notification: {e}")
            return None

    def _transform_qpu_data(self, qpu_data, toe_id=None):
        """Transform QPU data to the format required by Clouditor API."""
        import uuid
        from datetime import datetime, timezone

        # Generate fresh UUIDs and timestamp each time
        evidence_id = str(uuid.uuid4())
        qpu_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

        # Create a dictionary to easily access values by id from the source format
        data_dict = {}
        for item in qpu_data:
            if isinstance(item, dict) and "id" in item and "value" in item:
                data_dict[item["id"]] = item["value"]

        # Return the transformed data - NO outer "evidence" wrapper
        transformed = {
            "timestamp": current_time,
            "id": evidence_id,
            "targetOfEvaluationId": toe_id or "00000000-0000-0000-0000-000000000000",
            "toolId": "QPU Collector",
            "resource": {
                "qpu": {
                    "id": qpu_id,
                    "name": "FOKUS-QPU",
                    "oneQubitGateErrorRate": str(data_dict.get("OneQubitGateErrorRate", "9.999999999998899e-05")),
                    "twoQubitGateErrorRate": str(data_dict.get("TwoQubitGateErrorRate", "0.00019998999999992773")),
                    "spamErrorRate": str(data_dict.get("SPAMErrorRate", "9.999999999998899e-05")),
                    "errorCorrectionEnabled": data_dict.get("ErrorCorrectionEnabled", False),
                    "creationTime": current_time,
                    "raw": json.dumps([{"id": "1234"}])  # Keep this simple for now
                }
            }
        }

        return transformed