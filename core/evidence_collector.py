from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import uvicorn
import json
import os
import logging

app = FastAPI(title="Dummy Evidence Collector Endpoints")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "dummy_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/ai")
async def upload_ai(file: UploadFile = File(...)):
    """
    Dummy endpoint to receive AI evidence uploads.
    """
    file_location = os.path.join(UPLOAD_DIR, "ai_" + file.filename)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    return JSONResponse(
        content={
            "filename": file.filename,
            "saved_to": file_location,
            "message": "AI evidence file received successfully."
        }
    )

@app.post("/upload/qdt")
async def upload_qdt(request: Request):
    """
    Endpoint to receive QDT evidence as JSON data.
    This endpoint accepts the transformed QPU data from notification_push_QDT.
    """
    try:
        # Parse JSON data from the request
        qdt_data = await request.json()
        
        # Extract key information for logging
        toe_id = qdt_data.get("target_of_evaluation_id", "unknown")
        resource_id = qdt_data.get("resource", {}).get("id", "unknown")
        
        logger.info(f"Received QDT data for TOE: {toe_id}, Resource ID: {resource_id}")
        
        # Save the JSON data to a file
        os.makedirs(os.path.join(UPLOAD_DIR, "qdt_json"), exist_ok=True)
        file_location = os.path.join(UPLOAD_DIR, "qdt_json", f"qdt_{toe_id}_{resource_id}.json")
        
        with open(file_location, "w") as f:
            json.dump(qdt_data, f, indent=2)
        
        return JSONResponse(
            content={
                "toe_id": toe_id,
                "resource_id": resource_id,
                "saved_to": file_location,
                "message": "QDT evidence data received successfully."
            }
        )
    except Exception as e:
        logger.error(f"Error processing QDT data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Failed to process QDT data."
            }
        )

uvicorn.run(app, port=8002, host='0.0.0.0')