# ADD APPMAP HERE - BEFORE FastAPI imports
import os
# os.environ.setdefault("APPMAP", "true")
# os.environ.setdefault("APPMAP_CONFIG", "/home/abdul/DigitalTwin/Cobalt/SDT/appmap.yml")
# import appmap
# import appmap.fastapi
import requests
import uvicorn
import json
import logging

import time
import sys

from fastapi import Request, FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Dict
from contextlib import asynccontextmanager
from datetime import datetime
from core.controller import Controller
from core.config import IDS_CONNECTOR_HOST, IDS_CONNECTOR_PORT
import json
import multiprocessing
from multiprocessing import Process, Queue

# ==================== SDT Bearer Token Storage ====================
# In-memory token storage for SDT-Manager OAuth2 credentials
sdt_token_store: Dict = {
    "access_token": None,
    "client_id": None,
    "client_secret": None,
    "sdt_id": None,
    "components": {},
    "timestamp": None
}

ctrl = Controller()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define lifespan function
@asynccontextmanager
async def connection_startup(app: FastAPI):
    # Code that runs on startup
    logger.info("Deleting existing connection with Ditto during startup")
    # ctrl.connection_delete()

    logger.info("Automatically establishing new connection with Ditto during startup")
    try:
        response = ctrl.connection_create()
        if response.get("success"):
            inner = response.get("response", {})
            if inner.get("status") == 409:
                logger.info("Ditto connection already exists — reusing existing connection 'mqtt-connection_101'")
            else:
                logger.info("Ditto connection established successfully")
        else:
            logger.error(f"Failed to establish Ditto connection: {response.get('error')}")
    except Exception as e:
        logger.error(f"Failed to establish connection during startup: {str(e)}")

    yield  # This line separates startup from shutdown code

    # Code that runs on shutdown (if needed)
    # You can add cleanup code here

    # Code that runs on shutdown (if needed)
    # You can add cleanup code here


# Initialize FastAPI app
app = FastAPI(title="SDT Service Interface", version="0.2.7", lifespan=connection_startup)

# Pass token store to controller for use in authenticated requests
ctrl.set_token_store(sdt_token_store)

ctrl.run_ditto_listener()
# # Create a queue for communication between processes
# ditto_queue = Queue()

# # Function to be run in a separate process to listen to Ditto
# def ditto_listener_process(queue):
#     try:
#         logger.info("Starting Ditto listener process")
#         ctrl.listen_to_ditto(queue)
#     except Exception as e:
#         logger.error(f"Error in Ditto listener process: {str(e)}")

# # Function to continuously check for messages and print them
# def message_printer_process(queue):
#     logger.info("Starting message printer process")
#     try:
#         while True:
#             if not queue.empty():
#                 message = queue.get()
#                 logger.info(f"Received Ditto message: {message}")
#                 print(f"Ditto message: {message}")
#             time.sleep(0.1)  # Small sleep to prevent high CPU usage
#     except Exception as e:
#         logger.error(f"Error in message printer process: {str(e)}")

# # Start the listener process
# ditto_process = Process(target=ditto_listener_process, args=(ditto_queue,))
# ditto_process.daemon = True  # Ensure the process terminates when the main process ends
# ditto_process.start()
# logger.info(f"Ditto listener process started with PID: {ditto_process.pid}")

# # Start the message printer process
# printer_process = Process(target=message_printer_process, args=(ditto_queue,))
# printer_process.daemon = True
# printer_process.start()
# logger.info(f"Message printer process started with PID: {printer_process.pid}")

# # Function to retrieve messages from the queue
# @app.get("/api/SDT/ditto-messages")
# async def get_ditto_messages():
#     messages = []
#     while not ditto_queue.empty():
#         try:
#             messages.append(ditto_queue.get_nowait())
#         except:
#             break
#     return JSONResponse(content={"messages": messages})
# ==================== ENDPOINTS BY FUNCTIONAL AREA ====================
# Organization: Authentication > Core Operations > Connection > Evidence > Parent > Sync > Templates > Health


# ==================== 1. AUTHENTICATION ENDPOINTS ====================

@app.post("/api/SDT/auth/token", tags=["Authentication"])
async def receive_bearer_token(payload: Dict):
    """
    Receive OAuth2 Bearer token from SDT-Manager.
    This endpoint stores the token for authenticated communication with IDS-Connector.

    Args:
        payload: {
            "sdt_id": "abc123def456",
            "client_id": "oauth_client_xyz",
            "client_secret": "secret_xyz",
            "access_token": "eyJhbGc...",
            "components": {
                "sdt": "abc123def456",
                "ids_connector": "conn789",
                "watchtower": "wt012"
            }
        }

    Returns:
        JSONResponse: Confirmation that token was stored
    """
    try:
        global sdt_token_store

        # Validate required fields
        required_fields = ["sdt_id", "access_token", "client_id"]
        for field in required_fields:
            if field not in payload:
                logger.error(f"Missing required field in token payload: {field}")
                raise ValueError(f"Missing required field: {field}")

        access_token = payload.get("access_token")

        if not access_token:
            raise ValueError("access_token cannot be empty")

        # Store token in memory
        sdt_token_store = {
            "access_token": access_token,
            "client_id": payload.get("client_id"),
            "client_secret": payload.get("client_secret"),
            "sdt_id": payload.get("sdt_id"),
            "components": payload.get("components", {}),
            "timestamp": datetime.now().isoformat()
        }

        # Also update the controller's token store reference
        ctrl.set_token_store(sdt_token_store)

        sdt_id = payload.get("sdt_id")
        logger.info(f"Bearer token received and stored for SDT {sdt_id}")
        logger.debug(f"Token timestamp: {sdt_token_store['timestamp']}")

        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "message": "Bearer token stored successfully",
                "sdt_id": sdt_id,
                "components": list(sdt_token_store.get("components", {}).keys()),
                "timestamp": datetime.now().isoformat()
            }
        )

    except ValueError as e:
        logger.error(f"Validation error storing Bearer token: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error storing Bearer token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store token: {str(e)}")


@app.get("/api/SDT/auth/token/status", tags=["Authentication"])
async def get_token_status():
    """
    Get current status of stored Bearer token (without revealing secrets).

    Returns:
        JSONResponse: Token status with redacted secrets
    """
    token = sdt_token_store.get("access_token")

    if not token:
        return JSONResponse(
            status_code=200,
            content={
                "status": "unavailable",
                "message": "No Bearer token currently stored",
                "sdt_id": None,
                "has_token": False
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "available",
            "message": "Bearer token is stored and ready for IDS-Connector authentication",
            "sdt_id": sdt_token_store.get("sdt_id"),
            "client_id": sdt_token_store.get("client_id"),
            "components": list(sdt_token_store.get("components", {}).keys()),
            "has_token": True,
            "token_stored_at": sdt_token_store.get("timestamp"),
            "token_preview": f"{token[:20]}..." if len(token) > 20 else "***"
        }
    )


# ==================== 2. CORE OPERATIONS (CRUD) ====================

@app.post("/api/SDT/create/", status_code=201, tags=["Core Operations"])
async def create(
    request: Request,
    toe_id: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"),
    category: str = Query(default="BOMS", description="Category/type of payload (AI or QDT or BOMS)"),
    create_parent: bool = Query(default=True, description="Create/update parent thing")
):
    """
    Endpoint to create a new SDT artifacts in Ditto with optional parent thing management.

    Args:
        request (Request): The request object containing the SDT data.
        toe_id (str): Target of Evaluation ID
        category (str): Category/type of payload (Resource.(AI or QDT or BOMS))
        create_parent (bool): Whether to create/update parent thing

    Returns:
        JSONResponse: A JSON response containing the creation status and details.
    """
    try:
        logger.info(f"Received request to create SDT artifact with ID: {toe_id}, type: {category}, parent: {create_parent}")

        # Parse the request JSON payload
        payload = await request.json()
        payload_str = json.dumps(payload)
        logger.info(f"Processing payload for SDT artifact creation, size: {len(payload_str)} bytes")

        # Create the Digital Twin in Ditto (with parent thing management)
        result = ctrl.create_in_ditto(payload_str, toe_id, category, create_parent=create_parent)
        logger.info(f"SDT artifact created with result: {result}")

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "SDT artifact successfully created",
                "data": {
                    "toeId": toe_id,
                    "type": category,
                    "timestamp": time.time(),
                    "result": result
                }
            }
        )
    except Exception as e:
        logger.error(f"Error creating SDT artifact: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to create SDT artifact: {str(e)}",
                "timestamp": time.time()
            }
        )

@app.get("/api/SDT/read/", tags=["Core Operations"])
async def read_item(toe_id: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(..., description="Level of evidence to retrieve")):
    """
    Endpoint to read an item from the Digital Twin model.

    Args:
        toe_id (str): The ID of the item to be read.
        category (str): Category/type of the item.

    Returns:
        JSONResponse: A JSON response containing the item data or an error message.
    """
    try:
        response = ctrl.read_item(toe_id, category)

        if response.get("error"):
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": response.get("error", "Item not found"),
                    "timestamp": time.time()
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Item retrieved successfully",
                "data": response,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error reading item: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to read item: {str(e)}",
                "timestamp": time.time()
            }
        )

@app.put("/api/SDT/update/", tags=["Core Operations"])
async def update_item(request: Request, toe_id: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(..., description="Level of evidence to retrieve")):
    """
    Endpoint to update an item in the Digital Twin model.

    Args:
        toe_id (str): The ID of the item to be updated.
        category (str): Category/type of the item.
        request (Request): The request object containing the updated item data.

    Returns:
        JSONResponse: A JSON response containing the updated item data or an error message.
    """
    try:
        payload = await request.json()
        updated_item = ctrl.update_item(toe_id, category, payload)

        if updated_item.get("error"):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": updated_item.get("error", "Failed to update item"),
                    "timestamp": time.time()
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Item updated successfully",
                "data": updated_item,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to update item: {str(e)}",
                "timestamp": time.time()
            }
        )


@app.delete("/api/SDT/delete/", tags=["Core Operations"])
async def delete_item_endpoint(
    toe_id: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"),
    category: str = Query(..., description="Category/type of evidence to delete"),
    update_parent: bool = Query(default=True, description="Update parent thing to remove child reference")
):
    """
    Endpoint to delete an item from the Digital Twin model.

    This endpoint deletes a thing from Ditto and updates the parent thing to remove the reference.

    Args:
        toe_id (str): Target of Evaluation ID.
        category (str): Category/type of evidence to delete (AI, BOMS, QDT, etc.).
        update_parent (bool): Whether to update parent thing to remove child reference.

    Returns:
        JSONResponse: Deletion result with status and message.
    """
    logger.info(f"Received request to delete item: toe_id={toe_id}, category={category}, update_parent={update_parent}")

    try:
        result = ctrl.delete_item(toe_id, category, update_parent=update_parent)

        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": result.get("message", "Item deleted successfully"),
                    "data": {
                        "toe_id": toe_id,
                        "category": category
                    },
                    "timestamp": time.time()
                }
            )
        else:
            logger.error(f"Failed to delete item: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": result.get("error", "Unknown error during deletion"),
                    "timestamp": time.time()
                }
            )

    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to delete item: {str(e)}",
                "timestamp": time.time()
            }
        )


# ==================== 3. CONNECTION MANAGEMENT ====================

@app.get("/api/SDT/topology/")
async def get_topology(toeid: list[str] = Query(default=["00000000-0000-0000-0000-000000000000"], description="One or more TOE IDs to retrieve topology for")):
    """
    Returns all Digital Twin things for the given TOE IDs, proxied through SDT.
    Reads genesis things via list_child_things, then fetches each child via read_item_by_id.
    """
    try:
        items = []
        for toe_id in toeid:
            result = ctrl.list_child_things(toe_id)
            if result.get("success"):
                for child_id in result.get("child_things", {}).keys():
                    thing = ctrl.read_item_by_id(child_id)
                    if thing:
                        items.append(thing)
        return JSONResponse(content={"items": items, "count": len(items)})
    except Exception as e:
        logger.error(f"Error retrieving topology: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/SDT/connection/", tags=["Connection Management"])
async def connection():
    """
    Establish a connection with the Eclipse Ditto Digital Twin backend.

    Initializes MQTT connection to Ditto instance for real-time updates and notifications.

    Returns:
        JSONResponse: Connection status with Ditto server details
    """
    try:
        logger.info("Received request to establish a connection with the Digital Twin")

        # Establish the connection with the Digital Twin
        response = ctrl.connection_create()

        # Standardize response
        if isinstance(response, dict):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Connection successfully established with Digital Twin",
                    "data": response,
                    "timestamp": time.time()
                }
            )
        else:
            logger.info("Connection successfully established with the Digital Twin")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Connection successfully established with Digital Twin",
                    "timestamp": time.time()
                }
            )
    except Exception as e:
        logger.error(f"Error establishing connection: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to establish connection: {str(e)}",
                "timestamp": time.time()
            }
        )


# ==================== 4. EVIDENCE MANAGEMENT ====================

# ==================== 5. DATA SYNCHRONIZATION ====================

#============================ ENDPOINTS for EVIDENCE COLLECTION and FETCHING through IDS Connector ============================

# # OLD ENDPOINTS - COMMENTED OUT
# @app.get("/api/SDT/sync/github")
# async def sync_github_repository(
#     github_url: str = Query(default="https://github.com/arehmanq101/testevidenceAI", description="GitHub repository URL"),
#     toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"),
#     category: str = Query(default="AI", description="Category of evidence (AI, BOMS, etc.)")
# ):
#     """
#     Sync data from GitHub repository to Ditto instance.
#     Creates repository thing and updates parent thing.

#     Args:
#         github_url: The URL of the GitHub repository to clone
#         toeid: Target of Evaluation ID
#         category: Category/type of evidence

#     Returns:
#         JSONResponse: Sync results with details of created things
#     """
#     try:
#         logger.info(f"Starting GitHub sync for TOE: {toeid}, repository: {github_url}")

#         result = ctrl.sync_github_repository(github_url, toeid, category)

#         if result.get("success"):
#             return JSONResponse(
#                 status_code=200,
#                 content={
#                     "status": "success",
#                     "message": result.get("message"),
#                     "data": {
#                         "toe_id": toeid,
#                         "category": category,
#                         "github_url": github_url,
#                         "repository_name": result.get("repository_name"),
#                         "thing_id": result.get("thing_id"),
#                         "parent_updated": result.get("parent_updated", False),
#                         "timestamp": time.time()
#                     }
#                 }
#             )
#         else:
#             return JSONResponse(
#                 status_code=500,
#                 content={
#                     "status": "error",
#                     "message": result.get("error", "Failed to sync GitHub repository"),
#                     "toe_id": toeid
#                 }
#             )

#     except Exception as e:
#         logger.error(f"Error syncing GitHub repository: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# # @app.get("/api/SDT/sync")



# @app.get("/api/SDT/sync")
# async def sync_ids_connector(
#     data_source_url: str = "https://api.dataprovider.com/datasets/ai-models",
#     toeid: str = Query(default="00000000-0000-0000-0000-000000000000"),
#     category: str = Query(default="AI")
# ):
#     """
#     Triggers external data fetch from IDS connector or data provider API
#     """
#     logger.info(f"Triggering IDS connector sync from: {data_source_url}")
#
#     try:
#         # Forward to controller to handle IDS connector communication
#         result = ctrl.sync_ids_connector(data_source_url, toeid, category)
#         return result
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post("/api/SDT/receive")
# async def receive_data(
#     file: UploadFile = File(...),
#     toeid: str = Query(...),
#     category: str = Query(...),
#     metadata: str = Query(default="{}")
# ):
#     """
#     Receives files from external connector and processes them
#     """
#     logger.info(f"Receiving file: {file.filename} for TOE: {toeid}")
#
#     try:
#         # Save the uploaded file temporarily
#         file_content = await file.read()
#
#         # Forward to controller to handle file processing
#         result = ctrl.receive_and_process_file(
#             file_content,
#             file.filename,
#             toeid,
#             category,
#             metadata
#         )
#
#         return result
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/api/SDT/sync/webhook")
# async def sync_webhook_registration(
#     provider_id: str = "medical-ai-provider",
#     dataset_id: str = "breast-cancer-models-v2",
#     toeid: str = Query(default="00000000-0000-0000-0000-000000000000"),
#     category: str = Query(default="AI")
# ):
#     """
#     Registers for data updates from external provider via webhook
#     """
#     logger.info(f"Registering webhook for provider: {provider_id}")
#
#     try:
#         # Forward to controller to handle webhook registration
#         result = ctrl.register_webhook(
#             provider_id,
#             dataset_id,
#             toeid,
#             category,
#             f"http://your-sdt-api:8000/api/SDT/webhook/{toeid}"
#         )
#
#         return result
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/SDT/webhook/{toeid}")
# async def receive_webhook(toeid: str, request: Request):
#     """
#     Receives webhook notifications when new data is available
#     """
#     payload = await request.json()
#     logger.info(f"Webhook received for TOE: {toeid}")
#
#     try:
#         # Forward to controller to handle webhook processing
#         result = ctrl.process_webhook(toeid, payload)
#         return result
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# NEW IDS CONNECTOR ENDPOINT - Based on IDSconnector.yml specification

@app.get("/api/SDT/sync/ids", tags=["Data Synchronization"])
async def sync_from_ids_connector(
    data_path: str = Query(default="all", description="Path to data in IDS connector: 'all' to fetch all resources, or specific resource name (e.g., 'clouditorBOM')"),
    toe_id: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"),
    ids_connector_url: str = Query(default=None, description="IDS Connector base URL for artifact retrieval (optional, uses config if not provided)")
):
    """
    Sync artifacts from IDS connector to Ditto Digital Twin.

    Fetches evidence data from IDS connector and creates corresponding things in Ditto.

    Args:
        data_path: 'all' to get all resources, or specific resource name like 'clouditorBOM'
        toe_id: Target of Evaluation ID (UUID format)
        ids_connector_url: Base URL of IDS connector (optional, uses config if not provided)

    Returns:
        JSONResponse: Sync results with status, message, and created thing details
    """
    try:
        # Use config values if URL not provided
        if ids_connector_url is None:
            ids_connector_url = f"http://{IDS_CONNECTOR_HOST}:{IDS_CONNECTOR_PORT}"

        logger.info(f"Starting IDS connector sync for TOE: {toe_id}, data_path: {data_path}, URL: {ids_connector_url}")

        result = ctrl.sync_ids_connector(data_path, toe_id, ids_connector_url)

        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": result.get("message"),
                    "data": {
                        "toe_id": toe_id,
                        "data_path": data_path,
                        "artifacts_synced": len(result.get("results", [])),
                        "results": result.get("results", []),
                        "timestamp": time.time()
                    }
                }
            )
        else:
            error_msg = result.get("error", "Unknown error")
            status_code = 400 if "not found" in error_msg.lower() else 500
            return JSONResponse(
                status_code=status_code,
                content={
                    "status": "error",
                    "message": error_msg,
                    "detail": result.get("detail"),
                    "timestamp": time.time()
                }
            )

    except Exception as e:
        logger.error(f"Error in IDS sync endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )


#=====================================================Connector APIS ENDS=================================================


@app.get("/api/SDT/evidence/", tags=["Evidence Management"])
async def get_evidence(
    toe_id: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"),
    category: str = Query(None, description="Category/type of evidence to retrieve (AI, QDT, IDS_Evidence, CLOUD, etc.)"),
    evidence_type: str = Query(default="thing", description="Type of evidence to return: 'thing' (full thing), 'zip' (compressed), 'files' (specific files), 'specific' (filtered), 'auto' (auto-detect)"),
    files: str = Query(None, description="Comma-separated list of specific files to retrieve (used with evidence_type=files or specific)"),
    include_patterns: str = Query(None, description="Comma-separated include patterns for ZIP files (e.g., *.py,*.h5) - used with evidence_type=zip"),
    exclude_patterns: str = Query(None, description="Comma-separated exclude patterns for ZIP files (e.g., .git/*,*.pyc) - used with evidence_type=zip"),
    format: str = Query(default="json", description="Response format: 'json' returns JSON response, 'download' returns downloadable file"),
    transform: str = Query(None, description="Optional transform name (e.g., qpu_clouditor) or custom mapping JSON to apply to evidence"),
    include_features: str = Query(None, description="Comma-separated list of specific features to include in response (used with evidence_type=thing)"),
    filename: str = Query(None, description="Filter by specific filename within the evidence (for FILE category)")
):
    """
    Retrieve evidence from a Digital Twin with flexible options for filtering and formatting.

    Examples:
        - Get full thing: /api/SDT/evidence/?toe_id=123&category=AI
        - Get ZIP with patterns: /api/SDT/evidence/?toe_id=123&category=AI&evidence_type=zip&include_patterns=*.py,*.h5
        - Get specific files: /api/SDT/evidence/?toe_id=123&category=QDT&evidence_type=files&files=qpu_data.json
        - Get with transform: /api/SDT/evidence/?toe_id=123&category=QDT&evidence_type=files&files=qpu_data.json&transform=qpu_clouditor
        - Download as file: /api/SDT/evidence/?toe_id=123&category=AI&format=download

    Args:
        toe_id: Target of Evaluation ID (UUID)
        category: Category to filter (optional, e.g., AI, QDT, etc.)
        evidence_type: Type of evidence (thing, zip, files, specific, auto)
        files: Comma-separated list of files (for files/specific type)
        include_patterns: Include patterns for ZIP (for zip type)
        exclude_patterns: Exclude patterns for ZIP (for zip type)
        format: Response format (json or download)
        transform: Transform name or custom mapping JSON
        include_features: Features to include (for thing type)
        filename: Specific filename to filter by

    Returns:
        JSONResponse or FileResponse: Evidence data or downloadable file.
    """
    try:
        logger.info(f"Flexible evidence retrieval: toe_id={toe_id}, type={evidence_type}, format={format}")

        # Parse comma-separated parameters
        files_list = [f.strip() for f in files.split(",")] if files else None
        include_list = [p.strip() for p in include_patterns.split(",")] if include_patterns else None
        exclude_list = [p.strip() for p in exclude_patterns.split(",")] if exclude_patterns else None
        features_list = [f.strip() for f in include_features.split(",")] if include_features else None

        # Call flexible evidence retrieval
        result = ctrl.get_evidence_flexible(
            toe_id=toe_id,
            category=category,
            evidence_type=evidence_type,
            files=files_list,
            include_patterns=include_list,
            exclude_patterns=exclude_list,
            format=format,
            transform=transform,
            include_features=features_list,
            filename=filename
        )

        # Check if result is a download request
        if isinstance(result, dict) and result.get("download"):
            file_path = result.get("file_path")
            filename = result.get("filename")
            media_type = result.get("media_type", "application/octet-stream")

            if file_path and os.path.exists(file_path):
                return FileResponse(
                    path=file_path,
                    filename=filename,
                    media_type=media_type
                )
            else:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "error",
                        "message": "Evidence file not found",
                        "timestamp": time.time()
                    }
                )

        # Return JSON response
        if isinstance(result, dict) and result.get("status"):
            return JSONResponse(content=result)
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Evidence retrieved successfully",
                    "data": result,
                    "timestamp": time.time()
                }
            )

    except Exception as e:
        logger.error(f"Error retrieving evidence: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )


#============================ PARENT THING ENDPOINTS ============================

@app.post("/api/SDT/parent/create", tags=["Parent Thing Management"])
async def create_parent(
    toe_id: str = Query(..., description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"),
    request: Request = None
):
    """
    Create a parent thing for a Target of Evaluation (TOE) with optional metadata.

    Parent things aggregate child things and track relationships in the Digital Twin.

    Args:
        toe_id: Target of Evaluation ID (UUID)
        request: Optional request body with parent metadata

    Returns:
        JSONResponse: Parent thing creation result with status and thing ID
    """
    try:
        metadata = {}
        if request:
            try:
                metadata = await request.json()
            except Exception as e:
                logger.warning(f"Could not parse request metadata: {e}")

        result = ctrl.create_parent_thing(toe_id, metadata)

        status_code = 201 if result.get("action") == "created" else 200
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "success",
                "message": result.get("message", "Parent thing created/updated successfully"),
                "data": result,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error creating parent thing: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )

@app.get("/api/SDT/parent/read", tags=["Parent Thing Management"])
async def read_parent(toe_id: str = Query(..., description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)")):
    """
    Retrieve the parent thing for a Target of Evaluation.

    Returns the parent thing containing metadata and child thing references.

    Args:
        toe_id: Target of Evaluation ID (UUID)

    Returns:
        JSONResponse: Parent thing data with status 200, or 404 if not found
    """
    try:
        result = ctrl.get_parent_thing(toe_id)

        if result:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Parent thing retrieved successfully",
                    "data": result,
                    "timestamp": time.time()
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Parent thing not found",
                    "timestamp": time.time()
                }
            )
    except Exception as e:
        logger.error(f"Error reading parent thing: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )

@app.get("/api/SDT/parent/children", tags=["Parent Thing Management"])
async def list_children(toe_id: str = Query(..., description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)")):
    """
    List all child things under a parent thing.

    Returns a list of all child things/artifacts associated with the parent thing for a TOE.

    Args:
        toe_id: Target of Evaluation ID (UUID)

    Returns:
        JSONResponse: List of child things with count and statistics
    """
    try:
        result = ctrl.list_child_things(toe_id)

        # Ensure result has proper structure
        if isinstance(result, dict) and result.get("status"):
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Child things retrieved successfully",
                    "data": result,
                    "timestamp": time.time()
                }
            )
    except Exception as e:
        logger.error(f"Error listing child things: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )


#=====================================================Connector APIS ENDS=================================================


# ==================== 6. TEMPLATES MANAGEMENT ====================

@app.post("/api/SDT/upload-template", tags=["Templates Management"])
async def upload_template(file: UploadFile = File(...)):
    """
    Upload and load a new template configuration file.

    Uploads a template.json file to SDT/templates/ directory and automatically reloads
    all templates in the Evidence Provider for immediate use.

    Args:
        file: template.json file to upload (required)

    Returns:
        JSONResponse: Upload result with status and file details
    """
    try:
        # Path to save
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(template_dir, exist_ok=True)
        template_path = os.path.join(template_dir, "template.json")

        # Save the file
        with open(template_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Reload templates
        ctrl.ep._load_usecase_templates()

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Template uploaded and loaded successfully",
                "data": {
                    "filename": file.filename,
                    "size": len(content),
                    "path": template_path
                },
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error uploading template: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to upload template: {str(e)}",
                "timestamp": time.time()
            }
        )


# ==================== 7. HEALTH & STATUS ====================

@app.get("/api/SDT/health", tags=["Health & Status"])
async def health_check():
    """
    Check the health and operational status of the SDT service and container.

    Returns system metrics including memory usage, CPU count, disk space, and uptime.
    Useful for monitoring and orchestration systems.

    Returns:
        JSONResponse: Comprehensive health status with container metrics
    """
    try:
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "container": {}
        }

        # Get container resource stats if running in Docker
        if os.path.exists("/.dockerenv"):
            # We're in a Docker container
            try:
                # Memory usage
                with open("/proc/self/status") as f:
                    for line in f:
                        if "VmRSS" in line:
                            health_data["container"]["memory_usage_kb"] = int(line.split()[1])

                # CPU usage (simplified)
                health_data["container"]["cpu_count"] = os.cpu_count()

                # Disk space
                disk = os.statvfs("/")
                free_space_gb = (disk.f_bavail * disk.f_frsize) / (1024 ** 3)
                health_data["container"]["disk_free_gb"] = round(free_space_gb, 2)

                # Container uptime
                with open("/proc/uptime") as f:
                    uptime_seconds = float(f.read().split()[0])
                    health_data["container"]["uptime_seconds"] = uptime_seconds
            except Exception as e:
                health_data["container"]["metrics_error"] = str(e)
        else:
            health_data["container"]["is_docker"] = False

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Service is healthy",
                "data": health_data,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "timestamp": time.time()
            }
        )

# Run the application
# if __name__ == '__main__':
#     try:
#         print("Starting server with HTTPS...")
#         uvicorn.run(
#             app,
#             host='127.0.0.1',
#             port=8000,
#             # ssl_certfile="certs/cert.pem",
#             # ssl_keyfile="certs/key.pem",
#             log_level="debug"
#         )
#     except Exception as e:
#         print(f"Error starting HTTPS server: {str(e)}")
#         sys.exit(1)

# Wrap with AppMap middleware, enabling remote if you like
# app = appmap.fastapi.Middleware(app).init_app()
# app.add_middleware(AppMapMiddleware)

if __name__ == '__main__':
    uvicorn.run(app, port=8001, host='0.0.0.0')
