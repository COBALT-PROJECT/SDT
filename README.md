# Security Digital Twin (SDT) Service v0.2.7


## Overview

The Security Digital Twin (SDT) Service v0.2.5 is a centralized middleware for integrating, validating, and synchronizing security evidence from multiple sources (CycloneDX, OSCAL, ARM, Watchtower, Clouditor, GitHub, Quantum DT) into a Digital Twin platform (Eclipse Ditto). It now supports Template 3.0, advanced evidence packaging, flexible authentication, and custom transformation for automated security and compliance workflows.


## Architecture

**Core Modules:**

- **SDT-Manager-ADAPTOR**: Ingests and validates evidence (CycloneDX, OSCAL, ARM, etc.) from Target of Evaluation (ToE), then forwards to Controller.
- **SDT-CONTROLLER**: Orchestrates evidence flow, manages Digital Twin lifecycle, and routes data to Ditto and collectors.
- **SDT-EVIDENCE PROVIDER**: Prepares, transforms, and packages evidence for collectors (Watchtower, Clouditor, AIShield, SPECTRA, BOM Analyzer, Quantum DT, etc.) using Template 3.0.
- **SDT-TRANSLATOR**: Synchronizes changes and ingests data models for Ditto via connectors (IDS, GitHub, Webhook, Quantum).

**New in v0.2.7:**
- OAuth2 Bearer Token Authentication with SDT-Manager integration
- Automatic token injection for IDS-Connector requests
- Token status monitoring endpoints

**New in v0.2.5:**
- Template 3.0: Unified evidence combinations, flexible packaging, and transformation
- Advanced authentication: Bearer, API Key, OAuth2
- Custom mapping and variable substitution for evidence
- Collector integration with auto-routing and notification


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
  python SDT/sdt_service.py

Or use Docker:
  docker build -t sdt-service .
  docker run -p 8000:8000 -p 1883:1883 sdt-service


## API Reference

### Authentication Endpoints

- **Receive Bearer Token:**
  POST /auth/token
  - Stores OAuth2 credentials received from SDT-Manager
  - Used for authenticated communication with IDS-Connector
  
- **Check Token Status:**
  GET /auth/token/status
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
- **Collector Evidence Notification:**
  GET /api/SDT/evidence/
- **Parent Thing Management:**
  POST /api/SDT/parent/create, GET /api/SDT/parent/read
- **Health Check:**
  GET /api/SDT/health

### Example: Create a Digital Twin from CycloneDX
```bash
curl -X POST "http://127.0.0.1:8000/api/SDT/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example",
    "payload": {
      "bomFormat": "CycloneDX",
      "specVersion": "1.4",
      "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
      "version": 1,
      "components": []
    }
  }'
```

### Example: Fetch Evidence from GitHub
```bash
curl -X GET "http://127.0.0.1:8000/api/SDT/sync/github?github_url=https://github.com/username/repo.git&toeid=test-001&category=AI" \
  -H "accept: application/json"
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

## Bearer Token Authentication

The SDT component now supports OAuth2 Bearer token authentication for secure communication with IDS-Connector. Tokens are received from SDT-Manager and used automatically in all IDS-Connector API calls.

### How It Works

1. **SDT-Manager Distribution**: SDT-Manager registers SDT with Authentication Manager, obtains OAuth2 token
2. **Token Reception**: SDT receives token via `POST /auth/token` endpoint
3. **Token Storage**: Token stored in-memory for use in subsequent requests
4. **Automatic Authentication**: All IDS-Connector calls automatically include Bearer token
5. **Error Handling**: Enhanced error handling for authentication failures (401, 403)

### Example: Receive Token from SDT-Manager

```bash
curl -X POST "http://localhost:8080/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "sdt_id": "abc123def456",
    "access_token": "eyJhbGc...",
    "client_id": "oauth_client_xyz",
    "client_secret": "secret_xyz",
    "components": {"sdt": "abc123", "ids_connector": "conn789"}
  }'
```

### Example: Check Token Status

```bash
curl "http://localhost:8080/auth/token/status"
```

### Example: Sync IDS with Bearer Token (Automatic)

```bash
curl "http://localhost:8080/api/SDT/sync/ids?data_path=all&toeid=test-123"
# Bearer token is automatically included in the request
```

For detailed documentation, see [AUTHENTICATION_QUICK_START.md](AUTHENTICATION_QUICK_START.md)

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
