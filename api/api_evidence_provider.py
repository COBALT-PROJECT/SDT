from fastapi import FastAPI, Query
from typing import Optional
import uvicorn
from core.evidence_provider import EvidenceProvider

app = FastAPI()

@app.get("/evidence/watchtower/")
def get_evidence(toeid: str = Query(...), level: str = Query(...)):
    provider = EvidenceProvider()
    result = provider.get_evidence(toeid, level)
    return result


#if __name__ == '__main__':
uvicorn.run(app, port=8002, host='127.0.0.1')