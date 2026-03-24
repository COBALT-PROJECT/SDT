# SDT Bearer Token Authentication - Quick Start Guide

## Implementation Summary

The SDT component now supports OAuth2 Bearer token authentication for secure communication with IDS-Connector. Tokens are received from SDT-Manager and used automatically in all IDS-Connector API calls.

---

## Key Changes Made

### 1. **sdt_interface-2.py**

**Added token storage**:
```python
sdt_token_store: Dict = {
    "access_token": None,
    "client_id": None,
    "client_secret": None,
    "sdt_id": None,
    "components": {},
    "timestamp": None
}
```

**Added endpoints**:
- `POST /auth/token` - Receive and store token from SDT-Manager
- `GET /auth/token/status` - Check current token status

**Pass token to controller**:
```python
ctrl.set_token_store(sdt_token_store)
```

---

### 2. **core/controller.py**

**Added token management methods**:
```python
def set_token_store(token_store_dict)       # Store token reference
def get_auth_headers()                       # Get Authorization header with Bearer token
def has_bearer_token()                       # Check if token available
```

**Modified IDS-Connector calls**:
```python
# Now automatically includes Bearer token
auth_headers = self.get_auth_headers()
headers = {"Content-Type": "application/json", **auth_headers}
response = requests.get(url, params=params, headers=headers, timeout=30)
```

**Enhanced error handling**:
- `401 Unauthorized` - Invalid/expired token
- `403 Forbidden` - Token lacks permissions
- `404 Not Found` - Resource not found

---

## API Endpoints

### Receive Token
```
POST /auth/token
Content-Type: application/json

{
  "sdt_id": "abc123",
  "access_token": "eyJhbGc...",
  "client_id": "oauth_xyz",
  "client_secret": "secret_xyz",
  "components": {...}
}

Response: 200 OK
{
  "status": "ok",
  "message": "Bearer token stored successfully",
  "sdt_id": "abc123",
  "timestamp": "2026-03-23T10:30:00"
}
```

### Check Token Status
```
GET /auth/token/status

Response: 200 OK
{
  "status": "available",
  "sdt_id": "abc123",
  "has_token": true,
  "token_preview": "eyJhbGc...",
  "token_stored_at": "2026-03-23T10:30:00"
}
```

### Sync IDS (Now with Bearer Token)
```
GET /api/SDT/sync/ids?data_path=all&toeid=test-123

Response: 200 OK
{
  "status": "success",
  "message": "Synced X artifacts from IDS connector",
  "data": {
    "toe_id": "test-123",
    "artifacts_synced": 5,
    "results": [...]
  }
}
```

---

## Flow Diagram

```
1. SDT-Manager Distributes Token
   │
   POST /auth/token
   ├─> sdt_token_store updated (in-memory)
   └─> Controller notified via set_token_store()

2. SDT Makes IDS-Connector Request
   │
   GET /api/IDSconnector/get_data_request
   ├─> Controller calls get_auth_headers()
   ├─> Retrieves Bearer token from store
   ├─> Adds to Authorization header
   └─> Request: Authorization: Bearer eyJhbGc...

3. IDS-Connector Validates Token
   │
   ├─> Checks token against stored config
   ├─> Returns data if valid
   └─> Returns 401 if invalid
```

---

## Usage Example

### In SDT Code

```python
# Controller automatically handles token:
from core.controller import Controller

ctrl = Controller()

# (Token will be set via /auth/token endpoint)

# When calling IDS-Connector, token is used automatically:
result = ctrl.sync_ids_connector(
    data_path="all",
    toe_id="target-123",
    ids_connector_url="http://ids-connector:8004"
)

# Error handling for authentication issues:
if result.get("status_code") == 401:
    # Token is invalid or expired
    print("Please redeploy SDT with SDT-Manager")
```

### In API Requests

```bash
# 1. SDT-Manager sends token
curl -X POST http://sdt-service:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "sdt_id": "abc123",
    "access_token": "eyJhbGc...",
    "client_id": "client_xyz",
    "components": {"sdt": "abc123", "ids_connector": "conn456"}
  }'

# 2. Verify token stored
curl http://sdt-service:8080/auth/token/status

# 3. Use IDS-Connector (token applied automatically)
curl http://sdt-service:8080/api/SDT/sync/ids?data_path=all&toeid=test-123
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "status": "error",
  "error": "Unauthorized — Invalid or expired Bearer token",
  "detail": "IDS-Connector rejected authentication. Make sure SDT-Manager has delivered a valid token.",
  "status_code": 401
}
```

**Cause**: Token missing, expired, or invalid

**Solution**: 
- Check token status: `GET /auth/token/status`
- Redeploy with SDT-Manager to receive new token

### 403 Forbidden
```json
{
  "status": "error",
  "error": "Forbidden — Bearer token lacks required permissions",
  "status_code": 403
}
```

**Cause**: Token valid but doesn't have required scopes

**Solution**: Check Authentication Manager configuration for required scopes

### 404 Not Found
```json
{
  "status": "error",
  "error": "Resource not found: all",
  "detail": "..."
}
```

**Cause**: Data path doesn't exist in IDS-Connector

**Solution**: Check available data_path values in IDS-Connector API

---

## Ditto Authentication (Unchanged)

Ditto continues to use **basic authentication** (not Bearer tokens):

```python
session = requests.Session()
session.auth = ("ditto", "ditto")  # Basic auth only
response = session.put(ditto_url, json=data)
```

This is unchanged and intentional - Ditto has its own internal auth mechanism.

---

## Logging

Check SDT logs for authentication activity:

```bash
# Token received
[INFO] Bearer token received and stored for SDT abc123def456

# IDS-Connector call
[INFO] Calling IDS connector: http://ids-connector:8004/api/IDSconnector/get_data_request with Bearer token auth

# Authentication error
[ERROR] Unauthorized — Bearer token invalid or expired for IDS connector
```

---

## Testing the Implementation

### Manual Test

```bash
# 1. Start SDT
cd /home/sdtm/SDTM/SDT
python -m uvicorn sdt_interface-2:app --host 0.0.0.0 --port 8080

# 2. Send test token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "sdt_id": "test-sdt-001",
    "access_token": "'$TOKEN'",
    "client_id": "test-client",
    "components": {"sdt": "test-sdt-001", "ids_connector": "test-ids"}
  }'

# 3. Check status
curl http://localhost:8080/auth/token/status | jq .

# 4. Test IDS sync (if IDS-Connector is running)
curl http://localhost:8080/api/SDT/sync/ids?data_path=all&toeid=test-123 | jq .
```

---

## Troubleshooting Checklist

- [ ] Token endpoint is accessible: `curl http://sdt:8080/auth/token -X POST`
- [ ] Token was received successfully: `curl http://sdt:8080/auth/token/status`
- [ ] `has_token: true` in status response
- [ ] IDS-Connector is reachable: `curl http://ids-connector:8004/health`
- [ ] Bearer token is passed in requests (check logs for "Bearer token auth")
- [ ] Check SDT logs for error messages
- [ ] Verify SDT-Manager distributed token (check SDT-Manager logs)

---

## Files Changed

1. `sdt_interface-2.py` - Added token storage, endpoints, and initialization
2. `core/controller.py` - Added token management methods and authentication
3. `AUTHENTICATION_IMPLEMENTATION.md` - Full documentation (this file)

---

## Notes

- Tokens are stored **in-memory only** (not persisted to disk)
- Token is stored when SDT-Manager calls `POST /auth/token`
- Token is used **automatically** for all IDS-Connector requests
- No changes needed to existing endpoint code - token handling is transparent
- Ditto continues to use basic auth (`ditto:ditto`)
- IDS-Connector also uses the same token for EDC/backend authentication

---

## Support

For detailed information, see: `AUTHENTICATION_IMPLEMENTATION.md`
