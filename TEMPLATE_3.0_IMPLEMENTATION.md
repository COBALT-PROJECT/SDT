# Template 3.0 Implementation - Complete ✅

## Implementation Status: **FULLY IMPLEMENTED**

All Template 3.0 features have been successfully implemented in the SDT system.

---

## ✅ Implemented Features

### **1. Evidence Provider (`evidence_provider.py`)**

#### Core Template 3.0 Methods:
- ✅ `__init__()` - Initializes with MQTT subscriptions setup
- ✅ `_load_usecase_templates()` - Loads templates from template directories
- ✅ `_setup_mqtt_subscriptions()` - Configures MQTT subscriptions from templates
- ✅ `get_subscribed_collectors()` - Returns matching collectors for MQTT events
- ✅ `_topic_matches()` - Matches MQTT topics with wildcard support
- ✅ `_thing_matches_filters()` - Filters things by category, sourceType, file extensions
- ✅ `send_notification()` - Sends notifications to collectors based on template config
- ✅ `_prepare_evidence()` - Prepares evidence based on type (thing/zip/files)
- ✅ `_transform_payload()` - Transforms payloads (named transformers or custom mapping)
- ✅ `_apply_mapping()` - Applies ${variable} substitution in custom mappings

#### Evidence Preparation Methods:
- ✅ `_create_zip()` - Creates ZIP archives with file pattern filtering
- ✅ `_get_files()` - Extracts specific files from thing file tree
- ✅ `_prepare_zip_evidence()` - Legacy ZIP preparation (for backward compatibility)
- ✅ `_prepare_file_evidence()` - Legacy file preparation
- ✅ `_prepare_json_evidence()` - Legacy JSON preparation

#### Authentication Methods:
- ✅ `_get_auth_headers()` - Generates auth headers (Bearer, API Key, OAuth2)
- ✅ `_get_authentication_headers()` - Alternative auth header generation

#### Utility Methods:
- ✅ `_substitute_env_vars()` - Substitutes ${ENV_VAR} in strings
- ✅ `_substitute_env()` - Alias for environment variable substitution
- ✅ `_extract_value_by_path()` - Extracts nested values using dot notation
- ✅ `_apply_custom_mapping()` - Applies custom field mappings
- ✅ `_auto_retry()` - Auto-retry failed notifications with exponential backoff
- ✅ `_retry_notification()` - Alternative retry implementation

#### Transformer Methods:
- ✅ `_transform_qpu_data()` - Transforms QPU data to Clouditor format

#### Legacy Methods (Backward Compatibility):
- ✅ `get_usecase_template()` - Gets template for use case and category
- ✅ `process_query()` - Processes evidence queries
- ✅ `_get_fallback_template()` - Provides fallback templates
- ✅ `notification_push_AI()` - Legacy AI notification
- ✅ `notification_push_QDT()` - Legacy QDT notification

---

### **2. Controller Integration (`controller.py`)**

#### MQTT Listener:
- ✅ `listen_to_ditto()` - Enhanced with template-based routing
  - Checks for matching collectors using `get_subscribed_collectors()`
  - Routes to configured collectors via `send_notification()`
  - Falls back to legacy methods if no collectors match
  - Properly extracts thing_id, toe_id, category from MQTT messages

---

### **3. Template Files**

#### AI Use Case Template (`templates/AI usecase/template.json`):
```json
{
  "config_name": "AI usecase",
  "config_version": "3.0",
  "evidence_collectors": [
    {
      "collector_id": "aishield",
      "enabled": true,
      "categories": ["AI"],
      "mqtt": {
        "topics": [
          "ditto-cobalt/+/+/things/twin/events/created",
          "ditto-cobalt/+/+/things/twin/events/modified"
        ]
      },
      "endpoint": "http://localhost:8002/upload/ai",
      "evidence": {
        "type": "zip",
        "include": ["*.py", "*.h5", "*.ipynb", "*.txt"],
        "exclude": [".git/*", "__pycache__/*", "*.pyc"]
      }
    },
    {
      "collector_id": "spectra",
      "enabled": true,
      "categories": ["AI"],
      "mqtt": {
        "filters": {
          "file_extensions": [".csv", ".pkl"]
        }
      },
      "endpoint": "http://localhost:8003/api/spectra/evidence",
      "auth": {
        "type": "bearer",
        "token_env": "SPECTRA_TOKEN"
      },
      "evidence": {
        "type": "files",
        "files": ["dataset.csv", "model.pkl", "model.h5"]
      },
      "transform": {
        "toe_id": "${toe_id}",
        "project": "${repo_name}",
        "timestamp": "${clone_timestamp}",
        "files": "${files}"
      }
    }
  ],
  "defaults": {
    "retry_attempts": 3,
    "max_file_size_mb": 100,
    "timeout_seconds": 30
  }
}
```

#### Quantum Use Case Template (`templates/Quantum usecase/template.json`):
```json
{
  "config_name": "Quantum usecase",
  "config_version": "3.0",
  "evidence_collectors": [
    {
      "collector_id": "clouditor",
      "enabled": true,
      "categories": ["QDT"],
      "endpoint": "http://${CLOUDITOR_IP}:${CLOUDITOR_PORT}/v1/assessment/evidences",
      "auth": {
        "type": "oauth2",
        "token_url": "http://${CLOUDITOR_IP}:${CLOUDITOR_PORT}/v1/auth/token",
        "client_id": "clouditor",
        "client_secret_env": "CLOUDITOR_SECRET"
      },
      "evidence": {
        "type": "files",
        "files": ["qpu_data.json"]
      },
      "transform": {
        "id": "${toe_id}",
        "timestamp": "${clone_timestamp}",
        "toolId": "QPU-Scanner",
        "resource": {
          "id": "${toe_id}",
          "type": "QuantumProcessingUnit"
        },
        "qpu_data": "${files}"
      }
    },
    {
      "collector_id": "boms_collector",
      "enabled": true,
      "categories": ["BOMS"],
      "mqtt": {
        "filters": {
          "sourceType": ["cyclonedx", "spdx"]
        }
      },
      "endpoint": "http://localhost:8006/api/bom/analyze",
      "auth": {
        "type": "api_key",
        "key_env": "BOM_API_KEY"
      },
      "evidence": {
        "type": "thing",
        "include_features": ["components", "metadata"]
      }
    }
  ],
  "defaults": {
    "retry_attempts": 3,
    "max_file_size_mb": 50,
    "timeout_seconds": 45
  }
}
```

---

## 📊 Evidence Type Combinations

| Evidence Type | Packaging | Auth Type | Transform | Output Format | Use Case |
|---------------|-----------|-----------|-----------|---------------|----------|
| **thing** | JSON | None | None | Full Thing JSON | Simple storage |
| **thing** | JSON | API Key | None | Full Thing JSON | Authenticated storage |
| **thing** | JSON | None | Custom mapping | Transformed JSON | Custom format |
| **thing** | JSON | OAuth2 | Custom mapping | Transformed JSON | Secure custom format |
| **files** | JSON | None | None | File metadata array | File listing |
| **files** | JSON | Bearer | Custom mapping | Transformed files | Authenticated file data |
| **zip** | Multipart | None | None | ZIP archive | Full repository |
| **zip** | Multipart | API Key | None | ZIP archive | Authenticated archive |

---

## 🔐 Authentication Types Supported

### 1. **No Authentication**
```json
"auth": null
```

### 2. **Bearer Token**
```json
"auth": {
  "type": "bearer",
  "token_env": "API_TOKEN"
}
```
- Reads token from environment variable
- Adds header: `Authorization: Bearer <token>`

### 3. **API Key**
```json
"auth": {
  "type": "api_key",
  "key_env": "API_KEY"
}
```
- Reads key from environment variable
- Adds header: `X-API-Key: <key>`

### 4. **OAuth2 Client Credentials**
```json
"auth": {
  "type": "oauth2",
  "token_url": "http://auth-server/token",
  "client_id": "client_id",
  "client_secret_env": "CLIENT_SECRET"
}
```
- Gets token from authorization server
- Uses Basic Auth with client credentials
- Adds header: `Authorization: Bearer <access_token>`

---

## 🔄 Transform Options

### 1. **No Transform (Direct)**
```json
"transform": null
```
Sends evidence as-is without transformation.

### 2. **Named Transformer**
```json
"transform": "qpu_clouditor"
```
Calls method: `_transform_qpu_clouditor(evidence_data, toe_id)`

Available transformers:
- `qpu_clouditor` - Transform QPU data for Clouditor API
- Custom transformers can be added as methods

### 3. **Custom Field Mapping**
```json
"transform": {
  "toe_id": "${toe_id}",
  "project_name": "${repo_name}",
  "timestamp": "${clone_timestamp}",
  "files": "${files}",
  "custom_field": "static_value"
}
```
- Supports `${variable}` substitution from thing attributes
- Supports nested objects
- Supports static values

**Example Output:**
```json
{
  "toe_id": "test-001",
  "project_name": "my-ai-model",
  "timestamp": "2025-10-10T10:00:00Z",
  "files": [...],
  "custom_field": "static_value"
}
```

---

## 🎯 Variable Substitution

### Supported Variables:
- `${toe_id}` - Target of Evaluation ID
- `${repo_name}` - Repository name
- `${github}` - GitHub URL
- `${clone_timestamp}` - Clone timestamp
- `${category}` - Thing category
- `${sourceType}` - Source type (Repository, cyclonedx, etc.)
- `${files}` - Files array (for file-based evidence)
- Any attribute from thing.attributes

### Environment Variable Substitution:
```json
"endpoint": "http://${CLOUDITOR_IP}:${CLOUDITOR_PORT}/api/evidences"
```
Becomes: `http://10.160.101.137:8080/api/evidences`

---

## 🧪 Testing the System

### Test 1: Create AI Repository Thing
```bash
curl -X GET "http://localhost:8005/api/SDT/sync/github?github_url=https://github.com/test/ai-model&toeid=test-001&category=AI"
```

**Expected Flow:**
1. Repository cloned
2. Thing created in Ditto with category "AI"
3. MQTT event published
4. Template system identifies matching collectors (aishield, spectra)
5. AIShield receives ZIP of repository
6. SPECTRA receives specific files if present
7. All notifications sent automatically

### Test 2: Create QDT Thing
```bash
curl -X GET "http://localhost:8005/api/SDT/sync/github?github_url=https://github.com/test/qpu-data&toeid=test-qdt&category=QDT"
```

**Expected Flow:**
1. Repository cloned
2. Thing created with category "QDT"
3. MQTT event published
4. Clouditor collector matched
5. OAuth2 token obtained
6. qpu_data.json transformed using custom field mapping
7. Notification sent to Clouditor

---

## 🎨 Example Collectors

### Example 1: AI Shield (ZIP Archive)
- **Subscribes to:** AI category, Repository sourceType
- **Packages:** ZIP with *.py, *.h5, *.ipynb files
- **Excludes:** .git, __pycache__
- **Sends to:** http://localhost:8002/upload/ai
- **Format:** Multipart form data
- **Auth:** None

### Example 2: SPECTRA (Specific Files)
- **Subscribes to:** AI category with .csv or .pkl files
- **Packages:** dataset.csv, model.pkl, model.h5 only
- **Sends to:** http://localhost:8003/api/spectra/evidence
- **Format:** JSON with file metadata + custom transform
- **Auth:** Bearer token

### Example 3: Clouditor (QPU Data)
- **Subscribes to:** QDT category
- **Packages:** qpu_data.json
- **Sends to:** Clouditor evidence endpoint
- **Format:** Custom transformed QPU format
- **Auth:** OAuth2 client credentials
- **Transform:** Custom field mapping

### Example 4: BOM Analyzer
- **Subscribes to:** BOMS category, cyclonedx/spdx sourceType
- **Packages:** Full thing with components feature
- **Sends to:** http://localhost:8006/api/bom/analyze
- **Format:** Direct thing JSON
- **Auth:** API key

---

## ✅ Benefits

1. **Decoupling**: Collectors subscribe to events, no polling needed
2. **Flexibility**: Each collector defines its own requirements
3. **Scalability**: Add new collectors without code changes
4. **Security**: Multiple auth mechanisms supported
5. **Resilience**: Built-in retry logic with exponential backoff
6. **Efficiency**: Only relevant collectors are notified
7. **Maintainability**: Configuration-driven, not code-driven
8. **Backward Compatible**: Legacy methods still work

---

## 🚀 Next Steps

### To Add a New Evidence Collector:

1. **Create/Update Template JSON:**
```json
{
  "collector_id": "new_collector",
  "enabled": true,
  "categories": ["NEW_CATEGORY"],
  "endpoint": "http://localhost:8000/api/collect",
  "auth": { "type": "api_key", "key_env": "COLLECTOR_KEY" },
  "evidence": { "type": "thing" }
}
```

2. **Restart SDT Service** - Templates are loaded on startup

3. **Test:**
```bash
# Create thing with matching category
curl -X POST "http://localhost:8005/api/SDT/create" ...
```

4. **Verify:** Check logs for "Notifying collector: new_collector"

---

## 📝 Implementation Complete!

All Template 3.0 features are now fully implemented and ready for use. The system supports:

- ✅ MQTT-based event routing
- ✅ Template-driven collector configuration
- ✅ Multiple evidence types (thing, files, zip)
- ✅ Multiple authentication methods
- ✅ Custom transformations
- ✅ Variable substitution
- ✅ Auto-retry with exponential backoff
- ✅ Backward compatibility

The SDT system now has a **fully event-driven, configurable evidence notification architecture**! 🎉
