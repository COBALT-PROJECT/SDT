import requests
import uvicorn
import json
import logging
import os
import time
import sys

from fastapi import Request, FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from contextlib import asynccontextmanager
from core.controller import Controller
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
async def create(request: Request, toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), payload_type: str = Query(default="BOMS", description="Type of payload (AI or QDT)")):
    """
    Endpoint to create a new SDT artifacts in Ditto.
    
    Args:
        request (Request): The request object containing the SDT data.
        toeid (str): Target of Evaluation ID
        payload_type (str): Type of payload (Resource.(AI or QDT or BOMS)) 
        
    Returns:
        JSONResponse: A JSON response containing the creation status and details.
    """
    try:
        logger.info(f"Received request to create a new SDT artifact with ID: {toeid}, type: {payload_type}")
        
        # Parse the request JSON payload
        payload = await request.json()
        payload_str = json.dumps(payload)
        logger.info(f"Processing payload for SDT artifact creation, size: {len(payload_str)} bytes")
        
        # Create the Digital Twin in Ditto
        result = ctrl.create_in_ditto(payload_str, toeid, payload_type)
        logger.info(f"SDT artifact successfully created in Ditto with ID: {toeid}")
        
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



#============================ ENDPOINTS for EVIDENCE COLLECTION and FETCHING for AISHIELD and Quantum files ============================
    
@app.get("/api/SDT/sync/AI")
async def sync_ai_evidences(github_url_AI: str = "https://github.com/arehmanq101/testevidenceAI", toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(default= "AI", description="Level of evidence to retrieve")):
    """
    This endpont is used to sync data coming from connector to the Ditto instance.

    For Demo purposes, it is used to clone a repository from GitHub and create a Digital Twin in Ditto.
    Args:
        github_url (str): The URL of the GitHub repository to clone.
    Returns:
        dict: A dictionary containing a message with the local path where the file is saved.
    """
    logger.info("Received request to sync data from GitHub repository")

    try:
        ctrl.start_update_sync(github_url_AI, toeid, category)  # Start periodic sync every hour 
        logger.info(f"Starting sync for GitHub repository: {github_url_AI}")
        # return "Repo thing created and in sync with Ditto"
    
        # ctrl.sync_connector_AI(github_url_AI)
        # logger.info(f"Sync completed for AI repository: {github_url_AI}")



        return "Repo thing created in Ditto"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/api/SDT/sync/QDT")
async def sync_quantum_evidences(github_url_QDT: str = "https://github.com/COBALT-PROJECT/Quantum-UC", toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(default= "QDT", description="Level of evidence to retrieve")):
    """
    This endpont is used to sync data coming from connector to the Ditto instance.

    For Demo purposes, it is used to clone a repository from GitHub and create a Digital Twin in Ditto.
    Args:
        github_url (str): The URL of the GitHub repository to clone.
    Returns:
        dict: A dictionary containing a message with the local path where the file is saved.
    """
    logger.info("Received request to sync data from GitHub repository")

    try:
        ctrl.start_update_sync(github_url_QDT, toeid, category)  # Start periodic sync every hour 
        logger.info(f"Starting sync for GitHub repository: {github_url_QDT}")
        # return "Repo thing created and in sync with Ditto"

        # ctrl.sync_connector_QDT(github_url_QDT)
        logger.info(f"Sync completed for Quantum repository: {github_url_QDT}")



        return "Repo thing created in Ditto"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/SDT/evidence/")
async def get_evidence(toeid: str = Query(default="00000000-0000-0000-0000-000000000000", description="Target of Evaluation ID (UUID format: 00000000-0000-0000-0000-000000000000)"), category: str = Query(..., description="Level of evidence to retrieve")):
    """
    Get evidence from Watchtower for a specific TOE.
    
    Args:
        toeid (str): Target of Evaluation ID
     category (str): Level of evidence to retrieve
        
    Returns:
        FileResponse or dict: A zip file of evidence or an error message
    """
    return ctrl.get_evidence(toeid, category)


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

# uvicorn.run(app, port=8005, host='0.0.0.0')