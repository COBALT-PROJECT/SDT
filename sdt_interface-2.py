# ADD APPMAP HERE - BEFORE FastAPI imports
import os
os.environ.setdefault("APPMAP", "true")
os.environ.setdefault("APPMAP_CONFIG", "/home/abdul/DigitalTwin/Cobalt/SDT/appmap.yml")
import appmap
import appmap.fastapi
import requests
import uvicorn
import json
import logging

import time
import sys

from fastapi import Request, FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from contextlib import asynccontextmanager
from core.controller import Controller
from core.config import IDS_CONNECTOR_HOST, IDS_CONNECTOR_PORT
import json
import multiprocessing
from multiprocessing import Process, Queue




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
        # logger.info("Connection successfully established with Ditto during startup")
        print(response)
    except Exception as e:
        logger.error(f"Failed to establish connection during startup: {str(e)}")

    yield  # This line separates startup from shutdown code

    # Code that runs on shutdown (if needed)
    # You can add cleanup code here

    # Code that runs on shutdown (if needed)
    # You can add cleanup code here


# Initialize FastAPI app
app = FastAPI(title="SDT Service Interface", lifespan=connection_startup)


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
# # Root endpoint

# # Endpoint to create a new Security Digital Twin

@app.post("/api/SDT/create/", status_code=201)
async def create(
    request: Request, 
    toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), 
    payload_type: str = Query(default="BOMS", description="Type of payload (AI or QDT)"),
    create_genesis: bool = Query(default=True, description="Create/update genesis thing")
):
    """
    Endpoint to create a new SDT artifacts in Ditto with optional genesis thing management.

    Args:
        request (Request): The request object containing the SDT data.
        toeid (str): Target of Evaluation ID
        payload_type (str): Type of payload (Resource.(AI or QDT or BOMS))
        create_genesis (bool): Whether to create/update genesis thing

    Returns:
        JSONResponse: A JSON response containing the creation status and details.
    """
    try:
        logger.info(f"Received request to create SDT artifact with ID: {toeid}, type: {payload_type}, genesis: {create_genesis}")

        # Parse the request JSON payload
        payload = await request.json()
        payload_str = json.dumps(payload)
        logger.info(f"Processing payload for SDT artifact creation, size: {len(payload_str)} bytes")

        # Create the Digital Twin in Ditto (with genesis thing management)
        result = ctrl.create_in_ditto(payload_str, toeid, payload_type, create_genesis=create_genesis)
        logger.info(f"SDT artifact created with result: {result}")

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "SDT artifact successfully created",
                "data": {
                    "toeId": toeid,
                    "type": payload_type,
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

@app.get("/api/SDT/read/")
async def read_item(toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(..., description="Level of evidence to retrieve")):
    """
    Endpoint to read an item from the Digital Twin model.

    Args:
        item_id (str): The ID of the item to be read.

    Returns:
        JSONResponse: A JSON response containing the item data or an error message.
    """
    try:

        response = ctrl.read_item(toeid, category)
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error reading item: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.put("/api/SDT/update/")
async def update_item(request: Request, toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(..., description="Level of evidence to retrieve")):
    """
    Endpoint to update an item in the Digital Twin model.

    Args:
        item_id (str): The ID of the item to be updated.
        request (Request): The request object containing the updated item data.

    Returns:
        JSONResponse: A JSON response containing the updated item data or an error message.
    """
    try:
        payload = await request.json()

        updated_item = ctrl.update_item(toeid, category, payload)
        return JSONResponse(content=updated_item)
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/api/SDT/delete/")
async def delete_item(toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(..., description="Level of evidence to retrieve")):
    """
    Endpoint to delete an item from the Digital Twin model.

    Args:
        item_id (str): The ID of the item to be deleted.

    Returns:
        JSONResponse: A JSON response indicating success or an error message.
    """
    try:

        response = ctrl.delete_item(toeid, category)
        return JSONResponse(content={"message": "Item deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/SDT/connection/")
async def connection(request: Request):
    """
    Endpoint to establish a connection with the Digital Twin.

    Args:
        request (Request): The request object containing the connection data.

    Returns:
        str: A confirmation message indicating the connection was established.
    """
    logger.info("Received request to establish a connection with the Digital Twin")

    # # Parse the request JSON payload
    # payload = await request.json()
    # payload_str = json.dumps(payload)
    # logger.info(f"Processing payload for connection establishment")

    # Establish the connection with the Digital Twin
    response = ctrl.connection_create()
    logger.info("Connection successfully established with the Digital Twin")
    print(response)
    return response



#============================ ENDPOINTS for EVIDENCE COLLECTION and FETCHING through IDS Connector ============================

# OLD ENDPOINTS - COMMENTED OUT
@app.get("/api/SDT/sync/github")
async def sync_github_repository(
    github_url: str = Query(default="https://github.com/arehmanq101/testevidenceAI", description="GitHub repository URL"),
    toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), 
    category: str = Query(default="AI", description="Category of evidence (AI, BOMS, etc.)")
):
    """
    Sync data from GitHub repository to Ditto instance.
    Creates repository thing and updates genesis thing.
    
    Args:
        github_url: The URL of the GitHub repository to clone
        toeid: Target of Evaluation ID
        category: Category/type of evidence
        
    Returns:
        JSONResponse: Sync results with details of created things
    """
    try:
        logger.info(f"Starting GitHub sync for TOE: {toeid}, repository: {github_url}")
        
        result = ctrl.sync_github_repository(github_url, toeid, category)
        
        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": result.get("message"),
                    "data": {
                        "toe_id": toeid,
                        "category": category,
                        "github_url": github_url,
                        "repository_name": result.get("repository_name"),
                        "thing_id": result.get("thing_id"),
                        "genesis_updated": result.get("genesis_updated", False),
                        "timestamp": time.time()
                    }
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": result.get("error", "Failed to sync GitHub repository"),
                    "toe_id": toeid
                }
            )
            
    except Exception as e:
        logger.error(f"Error syncing GitHub repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

@app.get("/api/SDT/sync/ids")
async def sync_from_ids_connector(
    data_path: str = Query(default="all", description="Path to data in IDS connector ('all' or specific resource name)"),
    toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID"),
    ids_connector_url: str = Query(default=None, description="IDS Connector base URL (defaults to config)")
):
    """
    Sync artifacts from IDS connector
    
    Args:
        data_path: 'all' to get all resources, or specific resource name like 'clouditorBOM'
        toeid: Target of Evaluation ID
        ids_connector_url: Base URL of IDS connector (optional, uses config if not provided)
        
    Returns:
        JSONResponse: Sync results with details of created things
    """
    try:
        # Use config values if URL not provided
        if ids_connector_url is None:
            ids_connector_url = f"http://{IDS_CONNECTOR_HOST}:{IDS_CONNECTOR_PORT}"
        
        logger.info(f"Starting IDS connector sync for TOE: {toeid}, data_path: {data_path}, URL: {ids_connector_url}")
        
        result = ctrl.sync_ids_connector(data_path, toeid, ids_connector_url)
        
        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": result.get("message"),
                    "data": {
                        "toe_id": toeid,
                        "data_path": data_path,
                        "artifacts_synced": len(result.get("results", [])),
                        "results": result.get("results", []),
                        "timestamp": time.time()
                    }
                }
            )
        else:
            return JSONResponse(
                status_code=400 if "not found" in result.get("error", "").lower() else 500,
                content={
                    "status": "error",
                    "message": result.get("error"),
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


@app.get("/api/SDT/evidence/")
async def get_evidence(
    toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format)"),
    category: str = Query(None, description="Category to filter (AI, QDT, etc.)"),
    evidence_type: str = Query(default="thing", description="Evidence type: thing|zip|files|specific|auto"),
    files: str = Query(None, description="Comma-separated list of files to retrieve (for files/specific type)"),
    include_patterns: str = Query(None, description="Comma-separated include patterns for ZIP (e.g., *.py,*.h5)"),
    exclude_patterns: str = Query(None, description="Comma-separated exclude patterns for ZIP (e.g., .git/*,*.pyc)"),
    format: str = Query(default="json", description="Response format: json|download"),
    transform: str = Query(None, description="Transform name (e.g., qpu_clouditor) or custom mapping JSON"),
    include_features: str = Query(None, description="Comma-separated features to include (for thing type)")
):
    """
    Flexible endpoint to retrieve evidence from a Digital Twin.
    
    Examples:
        - Get full thing: /api/SDT/evidence/?toeid=123&category=AI
        - Get ZIP with patterns: /api/SDT/evidence/?toeid=123&category=AI&evidence_type=zip&include_patterns=*.py,*.h5
        - Get specific files: /api/SDT/evidence/?toeid=123&category=QDT&evidence_type=files&files=qpu_data.json
        - Get with transform: /api/SDT/evidence/?toeid=123&category=QDT&evidence_type=files&files=qpu_data.json&transform=qpu_clouditor
        - Download as file: /api/SDT/evidence/?toeid=123&category=AI&format=download

    Args:
        toeid: Target of Evaluation ID
        category: Category to filter (optional)
        evidence_type: Type of evidence (thing|zip|files|specific|auto)
        files: Comma-separated list of files (for files/specific type)
        include_patterns: Include patterns for ZIP (for zip type)
        exclude_patterns: Exclude patterns for ZIP (for zip type)
        format: Response format (json|download)
        transform: Transform name or custom mapping JSON
        include_features: Features to include (for thing type)

    Returns:
        JSONResponse or FileResponse: Evidence data or downloadable file.
    """
    try:
        logger.info(f"Flexible evidence retrieval: toeid={toeid}, type={evidence_type}, format={format}")
        
        # Parse comma-separated parameters
        files_list = [f.strip() for f in files.split(",")] if files else None
        include_list = [p.strip() for p in include_patterns.split(",")] if include_patterns else None
        exclude_list = [p.strip() for p in exclude_patterns.split(",")] if exclude_patterns else None
        features_list = [f.strip() for f in include_features.split(",")] if include_features else None
        
        # Call flexible evidence retrieval
        result = ctrl.get_evidence_flexible(
            toe_id=toeid,
            category=category,
            evidence_type=evidence_type,
            files=files_list,
            include_patterns=include_list,
            exclude_patterns=exclude_list,
            format=format,
            transform=transform,
            include_features=features_list
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
                    content={"status": "error", "message": "Evidence file not found"}
                )
        
        # Return JSON response
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error retrieving evidence: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


#============================ GENESIS THING ENDPOINTS ============================

@app.post("/api/SDT/genesis/create")
async def create_genesis(
    toeid: str = Query(..., description="Target of Evaluation ID"),
    request: Request = None
):
    """
    Explicitly create a genesis thing for a TOE ID with optional metadata.
    
    Args:
        toeid: Target of Evaluation ID
        request: Optional request body with metadata
        
    Returns:
        JSONResponse: Genesis thing creation result
    """
    try:
        metadata = {}
        if request:
            try:
                metadata = await request.json()
            except:
                pass
        
        result = ctrl.create_genesis_thing(toeid, metadata)
        
        return JSONResponse(
            status_code=201 if result.get("action") == "created" else 200,
            content=result
        )
    except Exception as e:
        logger.error(f"Error creating genesis thing: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/SDT/genesis/read")
async def read_genesis(toeid: str = Query(..., description="Target of Evaluation ID")):
    """
    Get the genesis thing for a TOE ID.
    
    Args:
        toeid: Target of Evaluation ID
        
    Returns:
        JSONResponse: Genesis thing data
    """
    try:
        result = ctrl.get_genesis_thing(toeid)
        
        if result:
            return JSONResponse(content=result)
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Genesis thing not found"}
            )
    except Exception as e:
        logger.error(f"Error reading genesis thing: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/SDT/genesis/children")
async def list_children(toeid: str = Query(..., description="Target of Evaluation ID")):
    """
    List all child things under a genesis thing.
    
    Args:
        toeid: Target of Evaluation ID
        
    Returns:
        JSONResponse: List of child things with statistics
    """
    try:
        result = ctrl.list_child_things(toeid)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error listing child things: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


#============================ ENDPOINTS FOR EVIDENCE COLLECTION for Quantum DT ============================


#============================ ENDPOINTS FOR EVIDENCE COLLECTION for Quantum DT ============================

# @app.get("/api/SDT/fetch/file/")
# async def fetch_file(github_url: str):
#     """
#     Fetch a file from a GitHub URL, save it locally, and return the local path.

#     Args:
#         github_url (str): The URL of the GitHub file to fetch.

#     Returns:
#         dict: A dictionary containing a message with the local path of the saved file.
#     """
#     try:
#         local_path = await adp.fetch_push_save_file(github_url)
#         return {"message": f"File saved at {local_path}"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.get("/api/SDT/evidence/clouditor/")
# def get_evidence(toeid: str = Query(...), category: str = Query(...)):
#     result = ctrl.get_evidence(toeid, category)
#     return result

@app.get("/api/SDT/health")
async def health_check():
    """
    Endpoint to check the health status of the Docker container and service.

    Returns:
        dict: A dictionary containing the health status of the service and container metrics.
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

        return JSONResponse(content=health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=500
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
app = appmap.fastapi.Middleware(app).init_app()
# app.add_middleware(AppMapMiddleware)

# if __name__ == '__main__':
#     uvicorn.run(app, port=8005, host='0.0.0.0')
