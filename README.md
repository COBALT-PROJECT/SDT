# Security Digital Twin (SDT) Service v0.2.1

## Overview

The Security Digital Twin (SDT) Service provides a centralized middleware between various security evidence sources of Target of Evaluation and the (Eclipse Ditto) as stored representaion in Digital Twin platform. This service offers a comprehensive REST API for validating CycloneDX payloads, managing Digital Twin instances, collecting security evidence, and Synchronizing with ToE through connector .

## Architecture

Currently three modules are implemented in the preliminary phase:

**SDT-Manager- ADAPTOR**: This module injests data from Target of Evaluation (ToE) e.g BOMS files in CycloneDX, validates the CycloneDX schema and sends to controller
        
**SDT - CONTROLLER**: Controller receives the data from adaptor, verifies and pushes it to for SDT (e.g Eclipse Ditto)

**SDT- EVIDENCE PROVIDER**: It curates the evidences for each collector e.g Watchtower, Clouditor 

**SDT- TRANSLATOR**: It synchronizes the changes through connector and ingest with appropriate data models for SDT (e.g Eclipse Ditto)

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

- **CycloneDX Integration**: Convert and validate CycloneDX payloads
- **Digital Twin Management**: Create, read, update, and delete Digital Twins in Eclipse Ditto
- **Evidence Collection**: Retrieve and package evidence from Watchtower and Clouditor
- **GitHub Integration**: Fetch files and clone repositories from GitHub
- **RESTful API**: Simple HTTP interface for all operations

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Eclipse Ditto instance
- Git (for repository operations)

### Setup

1. Clone the repository:
   git clone https://github.com/COBALT-PROJECT/SDT

2. Install dependencies:
  python setup.py

3. Run the service:
  python SDT/sdt_service.py

## API Reference

## Basic Operations for SDT Manager
### Create a Digital Twin from CycloneDX data
```ts
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


### Fetch a Evidence from Github repository
```ts
curl -X GET "http://127.0.0.1:8000/api/SDT/fetch/repo/?github_url=https://github.com/username/repo.git" \
  -H "accept: application/json"
```

## Basic Operations of SDT 

