
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
            
            
    def notification_push_QDT(self, file_path, toe_id=None, filename=None, media_type="application/json"):
        """
        Reads a QPU data JSON file, transforms it to the required format, and sends it to the QDT endpoint.
        """

        dummy_url = "http://localhost:8002/upload/qdt"
        
        # Read the JSON file
        try:
            with open(file_path, "r") as f:
                qpu_data = json.load(f)
            
            # Transform data
            transformed_data = self._transform_qpu_data(qpu_data, toe_id)
            
            # Send the transformed data
            try:
                response = requests.post(
                    dummy_url, 
                    json=transformed_data,
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"QDT notification sent, status: {response.status_code}")
                return response.status_code
            except Exception as e:
                logger.error(f"Failed to send QDT notification: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to process QPU data file: {e}")
            return None
            
    def _transform_qpu_data(self, qpu_data, toe_id=None):
        """
        Transforms QPU data from the source format to the target format.
        """
        
        # Create a dictionary to easily access values by id
        data_dict = {item["id"]: item["value"] for item in qpu_data}
        
        # Generate current timestamp in ISO format with timezone
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Create the transformed structure
        transformed = {
            "id": str(uuid.uuid4()),
            "timestamp": current_time,
            "target_of_evaluation_id": toe_id or "11111111-1111-1111-1111-111111111111",
            "toolId": "QPU Evidence Collector",
            "resource": {
                "@type": "type.googleapis.com/clouditor.ontology.v1.QPU",
                "creationTime": current_time,
                "id": str(uuid.uuid4()),
                "name": "FOKUS-QPU",
                "OneQubitErrorRate": str(data_dict.get("OneQubitGateErrorRate", 0.00001)),
                "TwoQubitErrorRate": str(data_dict.get("TwoQubitGateErrorRate", 0.00001)),
                "SpamErrorRate": str(data_dict.get("SPAMErrorRate", 0.00001)),
                "ErrorCorrectionEnabled": data_dict.get("ErrorCorrectionEnabled", True),
                "raw": json.dumps(qpu_data)
            }
        }
        
        return transformed
