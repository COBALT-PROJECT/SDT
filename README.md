# Security Digital Twin (SDT) Service v0.2.8


## Overview

The Security Digital Twin (SDT) Service v0.2.8 is a centralized middleware for integrating, validating, and synchronizing security evidence from multiple sources (CycloneDX, OSCAL, ARM, Watchtower, Clouditor, GitHub, Quantum DT) into a Digital Twin platform (Eclipse Ditto). It now supports Template 3.0, advanced evidence packaging, flexible authentication, token-based request authentication, and custom transformation for automated security and compliance workflows.


## Architecture

**Core Modules:**

- **SDT-Manager-ADAPTOR**: Ingests and validates evidence (CycloneDX, OSCAL, ARM, etc.) from Target of Evaluation (ToE), then forwards to Controller.
- **SDT-CONTROLLER**: Orchestrates evidence flow, manages Digital Twin lifecycle, and routes data to Ditto and collectors.
- **SDT-EVIDENCE PROVIDER**: Prepares, transforms, and packages evidence for collectors (Watchtower, Clouditor, AIShield, SPECTRA, BOM Analyzer, Quantum DT, etc.) using Template 3.0.
- **SDT-TRANSLATOR**: Synchronizes changes and ingests data models for Ditto via connectors (IDS, GitHub, Webhook, Quantum).

**New in v0.2.8:**
- **Token Authentication Middleware**: All endpoints (except auth/health) require Bearer token authentication
- **Split Evidence Endpoints**: GET /evidence/thing, /evidence/list, /evidence/download, GET /evidence/transform
- **File Discovery**: /evidence/list endpoint for discovering available files before download
- **Smart Download**: Intelligent file packaging (single file, ZIP archive, or multiple files)
- **Enhanced Security**: Global token verification with 401/403 error handling


## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [API Reference](#api-reference)
  - [Basic Operations](#basic-operations)
  - [Digital Twin Management](#digital-twin-management)
- [Usage Examples](#usage-examples)




## Features

- **Bearer Token Authentication**: Middleware-based token verification for all protected endpoints
- **Split Evidence Endpoints**: Specialized endpoints for metadata, file discovery, downloads, and transformations
- **Template 3.0 Evidence Combinations**: 22+ combinations for thing, files, zip, with flexible authentication and transformation
- **CycloneDX, OSCAL, ARM Integration**: Validate and transform evidence from multiple formats
- **Digital Twin Management**: Full CRUD for Eclipse Ditto instances
- **Custom Transformation**: Named transformers and custom field mapping with variable substitution
- **GitHub & IDS Connector**: Fetch, clone, and synchronize repositories and external data sources



## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Eclipse Ditto instance
- Git
- Mosquitto MQTT broker

### Setup

1. Clone the repository:
  git clone https://github.com/COBALT-PROJECT/SDT

2. Install dependencies:
  pip install -r requirements.txt

3. Run the service:
  python SDT/sdt_interface-3.py

Or use Docker:
  docker build -t sdt-service .
  docker run -p 8000:8000 -p 1883:1883 sdt-service


## API Reference

### Authentication Endpoints

- **Receive Bearer Token:**
  POST /api/SDT/auth/token
  - Stores OAuth2 credentials received from SDT-Manager
  - Used for authenticated communication with IDS-Connector
  
- **Check Token Status:**
  GET /api/SDT/auth/token/status
  - Returns token availability and components (secrets redacted)
  - Useful for monitoring and debugging

### Core Endpoints

- **Create Digital Twin from CycloneDX/OSCAL/ARM:**
  POST /api/SDT/create/
- **Read/Update/Delete Digital Twin:**
  GET /api/SDT/read/, PUT /api/SDT/update/, DELETE /api/SDT/delete/
- **Sync Evidence from GitHub/IDS Connector:**
  GET /api/SDT/sync/github, GET /api/SDT/sync/ids
  - IDS sync now uses Bearer token for authentication

### Evidence Endpoints (Split for Better UX)

- **Get Thing Metadata:**
  GET /api/SDT/evidence/thing
  - Parameters: toe_id, category (optional), include_features (optional)
  - Returns: Complete thing object with metadata
  - Use Case: View thing details and attributes

- **List Evidence Files:**
  GET /api/SDT/evidence/list
  - Parameters: toe_id, category (optional), pattern (optional glob), recursive (optional)
  - Returns: File listing with metadata (name, size, type, timestamps)
  - Use Case: Discover available files before downloading

- **Download Evidence Files:**
  GET /api/SDT/evidence/download
  - Parameters: toe_id, files (optional, comma-separated), category (optional)
  - Smart Logic: Single file (raw), multiple files or no files (ZIP archive)
  - Returns: FileResponse (binary) or error JSON
  - Use Case: Download specific file(s) with intelligent packaging

- **Transform Evidence Data:**
  GET /api/SDT/evidence/transform
  - Parameters: toe_id, transform, category (optional), files (optional), target_format (optional)
  - Returns: Transformed data (JSON, XML, etc.)
  - Transform Types: qpu_clouditor, custom mappings
  - Use Case: Apply data transformations for downstream processors

### Parent Thing Management

- **Create Parent Thing:**
  POST /api/SDT/parent/create
  - Aggregates child things for hierarchical organization
  
- **Read Parent Thing:**
  GET /api/SDT/parent/read
  
- **List Child Things:**
  GET /api/SDT/parent/children

### Additional Endpoints

- **Upload Template:**
  POST /api/SDT/upload-template
  
- **Health Check:**
  GET /api/SDT/health

### Example: Create a Digital Twin from CycloneDX

```bash
# First, receive and store token
curl -X POST "http://localhost:8000/api/SDT/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "sdt_id": "sdt-001",
    "access_token": "eyJhbGc...",
    "client_id": "oauth_client",
    "client_secret": "secret"
  }'

# Then create Digital Twin with token
curl -X POST "http://localhost:8000/api/SDT/create/?toe_id=001&category=BOMS" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "bomFormat": "CycloneDX",
    "specVersion": "1.4",
    "version": 1,
    "components": []
  }'
```

### Example: Get Evidence with Token

```bash
curl -X GET "http://localhost:8000/api/SDT/evidence/thing?toe_id=001&category=QDT" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Example: List Files Before Download

```bash
curl -X GET "http://localhost:8000/api/SDT/evidence/list?toe_id=001" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Example: Download Evidence Files

```bash
curl -X GET "http://localhost:8000/api/SDT/evidence/download?toe_id=001&files=data.json" \
  -H "Authorization: Bearer eyJhbGc..." \
  -o evidence.zip
```

## Template 3.0 Evidence Combinations

Supports 22+ combinations for evidence packaging, authentication, and transformation. See `EVIDENCE_COMBINATIONS_TABLE.md` for full matrix.

| Evidence Type | Packaging | Auth | Transform | Output | Use Case |
|--------------|-----------|------|-----------|--------|----------|
| thing        | JSON      | Any  | Any       | Full/partial thing | Storage, analysis |
| files        | JSON      | Any  | Any       | File metadata      | File analysis |
| zip          | Multipart | Any  | None      | ZIP archive        | Repo scan |

**Authentication:** None, Bearer, API Key, OAuth2
**Transformation:** Direct, named transformer, custom mapping with variable substitution

**Collector Examples:**
- AIShield: ZIP archive, no auth
- SPECTRA: Specific files, Bearer token, custom mapping
- Clouditor: QPU data, OAuth2, custom mapping
- BOM Analyzer: Thing with features, API Key

## Usage Examples

### AI Repository Scan
1. Create thing from GitHub repo (category: AI)
2. AIShield receives ZIP archive
3. SPECTRA receives selected files with custom mapping

### Quantum DT Evidence
1. Create thing from Quantum repo (category: QDT)
2. Clouditor receives QPU data with OAuth2 authentication

### BOM Analysis
1. Create thing from CycloneDX BOM
2. BOM Analyzer receives filtered thing JSON with API Key

## Request-Level Token Authentication Middleware (v0.2.8)

All API endpoints (except authentication and health checks) now enforce Bearer token authentication via middleware. This provides global security without requiring token checks in individual endpoint handlers.

### How It Works

1. **Token Reception**: Client calls `POST /api/SDT/auth/token` to store OAuth2 token
2. **Token Storage**: Token stored in-memory in `sdt_token_store`
3. **Request Interception**: Middleware intercepts all incoming requests
4. **Unprotected Endpoints**: Auth and health endpoints skip validation:
   - `POST /api/SDT/auth/token` - Receive token
   - `GET /api/SDT/auth/token/status` - Check token status
   - `GET /api/SDT/health` - Health check
5. **Protected Endpoints**: All other endpoints require valid Bearer token
6. **Token Validation**: Extracts and validates token from `Authorization: Bearer {token}` header
7. **Response**: Returns 401 if token missing, invalid, or expired

### Required Request Header

```
Authorization: Bearer {access_token}
```

### Example: Call Protected Endpoint with Token

```bash
curl -X GET "http://localhost:8000/api/SDT/evidence/thing?toe_id=123&category=QDT" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Error Responses

**401 Unauthorized - Missing Bearer Token:**
```json
{
  "status": "error",
  "message": "Missing or invalid Bearer token",
  "timestamp": 1711353600.123
}
```

**401 Unauthorized - Invalid Token:**
```json
{
  "status": "error",
  "message": "Invalid or expired token",
  "timestamp": 1711353600.123
}
```

## Changelog v0.2.8

- **Request-Level Token Authentication Middleware**: All protected endpoints require Bearer token in Authorization header
- **Global Security**: Token validation via middleware (no per-endpoint overhead)
- **Split Evidence Endpoints**: Improved UX with specialized endpoints for different evidence operations
  - GET /api/SDT/evidence/thing - Metadata retrieval
  - GET /api/SDT/evidence/list - File discovery with pattern matching
  - GET /api/SDT/evidence/download - Smart file download (raw or ZIP)
  - GET /api/SDT/evidence/transform - Data transformation engine
- **File Discovery**: New /evidence/list endpoint supports pattern matching and recursive file listing
- **Smart Download**: Intelligent packaging logic (single file / multiple files / archive)
- **Enhanced Status Codes**: 401 for auth failures, proper 404 for not found (no 200 errors)

## Changelog v0.2.7

- **OAuth2 Bearer Token Authentication**: Secure communication with IDS-Connector via SDT-Manager
- **Token Status Endpoint**: Monitor token availability
- **Automatic Bearer Token Injection**: All IDS-Connector calls automatically authenticated
- **Enhanced Error Handling**: Detailed errors for authentication failures (401, 403, 404)

## Changelog v0.2.5

- Template 3.0: Unified evidence combinations and flexible packaging
- Advanced authentication: Bearer, API Key, OAuth2
- Custom mapping and variable substitution for evidence
- Collector integration with auto-routing and notification
- Quantum DT and QPU evidence support
- Improved Dockerfile and MQTT integration
- Enhanced API endpoints and health checks
