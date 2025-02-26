import requests
import uvicorn
import json
import logging
import os
import time

from adapter import *
from fastapi import Request, FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
adapter = DTModelAdapter()

@app.get("/")
async def root():
    return {"message": "DT Model Adapter API"}

@app.post("/api/clouditor2dt/")
async def clouditor2dt(request: Request):
    payload = await request.json()
    adapter = DTModelAdapter()
    translated = adapter.from_cloud(payload)

    ret = []
    for i in translated:
        payload = json.loads(i)
        r = adapter.send_to_controller1(payload)
        logger.info(r.json())
        ret.append(payload)
    return JSONResponse(content=ret)

@app.post("/api/cbom2dt/")
async def cbom2dt(file: UploadFile = File(...)):
    """
    Endpoint to upload a CBOM (Cryptographic Bill of Materials) file and convert it using from_CCM_cbom.

    Args:
        file (UploadFile): The CBOM file to be uploaded.

    Returns:
        dict: A dictionary representing the converted CBOM.
    """
    try:
        # Read the file content
        content = await file.read()
        payload = json.loads(content)
        
        # Use the adapter to convert the CBOM
        adapter = DTModelAdapter()
        converted = adapter.from_CCM_cbom(payload)
        
        # Save the converted output to sdt_output directory
        output_dir = "/home/abdul/DigitalTwin/Cobalt/SDT/sdt_output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"cbom_sdt_thing_{int(time.time())}.json")
        with open(output_path, "w") as f:
            json.dump(converted, f, indent=4)
        
        # Send the converted payload to the controller
        response = adapter.send_to_controller1(converted)
        logger.info(response.json())
        
        return JSONResponse(content={"message": "Sent to Ditto", "response": response.json()})
    except Exception as e:
        logger.error(f"Error processing CBOM file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/api/sbom2dt/")
async def sbom2dt(file: UploadFile = File(...)):
    """
    Endpoint to upload an SBOM (Software Bill of Materials) file and convert it using from_CCM_sbom.

    Args:
        file (UploadFile): The SBOM file to be uploaded.

    Returns:
        dict: A dictionary representing the converted SBOM.
    """
    try:
        # Read the file content
        content = await file.read()
        payload = json.loads(content)
        
        # Use the adapter to convert the SBOM
        adapter = DTModelAdapter()
        converted = adapter.from_CCM_sbom(payload)
        
        # Save the converted output to sdt_output directory
        output_dir = "/home/abdul/DigitalTwin/Cobalt/SDT/sdt_output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "sbom_sdt_thing.json")
        with open(output_path, "w") as f:
            json.dump(converted, f, indent=4)
        
        # Send the converted payload to the controller
        response = adapter.send_to_controller1(converted)
        logger.info(response.json())
        
        return JSONResponse(content={"message": "Sent to Ditto", "response": response.json()})
    except Exception as e:
        logger.error(f"Error processing SBOM file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/api/SDT/create/")
async def cyclone2dt(request: Request):
    """
    Endpoint to validate and convert a CycloneDX payload.

    Args:
        request (Request): The request object containing the CycloneDX payload.

    Returns:
        JSONResponse: A JSON response containing the converted payload or an error message.
    """
    try:

        # Receive the payload and extract the name and json_payload
        payload = await request.json()
        name = payload.get("name")
        json_payload = payload.get("payload")

        if not name or not json_payload:
            raise ValueError("Invalid payload: 'name' and 'payload' fields are required")

        
        # Validate the CycloneDX payload using the adapter's validate_cyclone method
        if validate_cyclone(json_payload):
            adapter = DTModelAdapter()    
            # Send the converted payload to the controller
            # Convert the CycloneDX payload using the adapter's from_cyclone method
            converted, urn, bom = from_cyclone(json_payload, name)
            response = adapter.send_to_controller(converted)
            logger.info(response.json())
        else:
            raise ValueError("Invalid CycloneDX payload")


        # # Ensure bom and urn are not None
        # if bom is None:
        #     bom = "bom"
        # if urn is None:
        #     urn = "urn"

        # # Save the converted output to sdt_output directory using the provided name
        # output_dir = "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/sdt_output"
        # os.makedirs(output_dir, exist_ok=True)
        # output_path = os.path.join(output_dir, f"sdt_thing_{bom}_{urn}.json")
        # with open(output_path, "w") as f:
        #     json.dump(converted, f, indent=4)


        
        return JSONResponse(content={"message": "Sent to Ditto", "response": response.json()})
    except Exception as e:
        logger.error(f"Error processing SBOM file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


# @app.get("/api/SDT/read/{item_id}")
# async def read_item(item_id: str):
#     """
#     Endpoint to read an item from the Digital Twin model.

#     Args:
#         item_id (str): The ID of the item to be read.

#     Returns:
#         JSONResponse: A JSON response containing the item data or an error message.
#     """
#     try:
#         adapter = DTModelAdapter()
#         item = adapter.read_item(item_id)
#         return JSONResponse(content=item)
#     except Exception as e:
#         logger.error(f"Error reading item: {e}")
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.put("/api/SDT/update/{item_id}")
# async def update_item(item_id: str, request: Request):
#     """
#     Endpoint to update an item in the Digital Twin model.

#     Args:
#         item_id (str): The ID of the item to be updated.
#         request (Request): The request object containing the updated item data.

#     Returns:
#         JSONResponse: A JSON response containing the updated item data or an error message.
#     """
#     try:
#         payload = await request.json()
#         adapter = DTModelAdapter()
#         updated_item = adapter.update_item(item_id, payload)
#         return JSONResponse(content=updated_item)
#     except Exception as e:
#         logger.error(f"Error updating item: {e}")
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.delete("/api/SDT/delete/{item_id}")
# async def delete_item(item_id: str):
#     """
#     Endpoint to delete an item from the Digital Twin model.

#     Args:
#         item_id (str): The ID of the item to be deleted.

#     Returns:
#         JSONResponse: A JSON response indicating success or an error message.
#     """
#     try:
#         adapter = DTModelAdapter()
#         adapter.delete_item(item_id)
#         return JSONResponse(content={"message": "Item deleted successfully"})
#     except Exception as e:
#         logger.error(f"Error deleting item: {e}")
#         return JSONResponse(content={"error": str(e)}, status_code=500)

#if __name__ == '__main__':
uvicorn.run(app, port=8001, host='127.0.0.1')

