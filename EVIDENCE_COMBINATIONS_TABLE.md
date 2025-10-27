# Template 3.0 - Evidence Combinations Reference Table

## 📊 All Possible Evidence Combinations

| # | Evidence Type | Auth Type | Transform Type | Packaging Format | Output Example | Use Case |
|---|--------------|-----------|----------------|------------------|----------------|----------|
| 1 | `thing` | None | None | JSON | `{"thingId": "...", "attributes": {...}, "features": {...}}` | Simple thing storage |
| 2 | `thing` | Bearer | None | JSON | Full thing JSON | Authenticated thing storage |
| 3 | `thing` | API Key | None | JSON | Full thing JSON | API key protected storage |
| 4 | `thing` | OAuth2 | None | JSON | Full thing JSON | OAuth2 protected storage |
| 5 | `thing` | None | Custom mapping | JSON | `{"toe_id": "...", "custom": "..."}` | Custom format transformation |
| 6 | `thing` | Bearer | Custom mapping | JSON | Transformed JSON | Secure custom format |
| 7 | `thing` | API Key | Custom mapping | JSON | Transformed JSON | API key + custom format |
| 8 | `thing` | OAuth2 | Custom mapping | JSON | Transformed JSON | OAuth2 + custom format |
| 9 | `thing` (with `include_features`) | None | None | JSON | `{"thingId": "...", "features": {"selected": {...}}}` | Partial thing data |
| 10 | `thing` (with `include_features`) | Bearer | Custom mapping | JSON | Transformed selected features | Secure partial data |
| 11 | `files` | None | None | JSON | `{"files": [{"name": "...", "content": "...", "hash": "..."}]}` | File metadata listing |
| 12 | `files` | Bearer | None | JSON | File metadata array | Authenticated file listing |
| 13 | `files` | API Key | None | JSON | File metadata array | API key file listing |
| 14 | `files` | OAuth2 | None | JSON | File metadata array | OAuth2 file listing |
| 15 | `files` | None | Custom mapping | JSON | `{"toe_id": "...", "files": [...]}` | Custom file format |
| 16 | `files` | Bearer | Custom mapping | JSON | Transformed files | Secure custom file format |
| 17 | `files` | API Key | Custom mapping | JSON | Transformed files | API key + custom file format |
| 18 | `files` | OAuth2 | Custom mapping | JSON | Transformed files | OAuth2 + custom file format (QPU use case) |
| 19 | `zip` | None | None | Multipart | ZIP file binary | Repository archive |
| 20 | `zip` | Bearer | None | Multipart | ZIP file binary | Authenticated archive |
| 21 | `zip` | API Key | None | Multipart | ZIP file binary | API key protected archive |
| 22 | `zip` | OAuth2 | None | Multipart | ZIP file binary | OAuth2 protected archive |

---

## 🎯 Evidence Type Details

### 1. `type: "thing"` - Full Thing or Selected Features

#### Basic Usage:
```json
"evidence": {
  "type": "thing"
}
```

**Output:** Complete Thing JSON
```json
{
  "thingId": "cobalt.sdt:toe-123-AI-...",
  "policyId": "cobalt:policy",
  "attributes": {
    "toe_id": "123",
    "category": "AI",
    "repo_name": "my-model"
  },
  "features": {
    "repository": {...},
    "Repository_file_tree": {...}
  }
}
```

#### With Feature Selection:
```json
"evidence": {
  "type": "thing",
  "include_features": ["repository", "components"]
}
```

**Output:** Filtered Thing JSON
```json
{
  "thingId": "cobalt.sdt:toe-123-AI-...",
  "attributes": {...},
  "features": {
    "repository": {...},
    "components": {...}
  }
}
```

---

### 2. `type: "files"` - Specific Named Files

```json
"evidence": {
  "type": "files",
  "files": ["dataset.csv", "model.pkl", "qpu_data.json"]
}
```

**Output:** JSON with file content and metadata
```json
{
  "files": [
    {
      "name": "dataset.csv",
      "path": "/evidence/dataset.csv",
      "content": "col1,col2\n1,2\n3,4",
      "hash": "sha256:abc123...",
      "size": 1024
    },
    {
      "name": "model.pkl",
      "path": "/evidence/model.pkl",
      "content": "...",
      "hash": "sha256:def456...",
      "size": 2048
    }
  ]
}
```

---

### 3. `type: "zip"` - ZIP Archive with Pattern Filtering

```json
"evidence": {
  "type": "zip",
  "include": ["*.py", "*.h5", "*.ipynb"],
  "exclude": [".git/*", "__pycache__/*", "*.pyc"]
}
```

**Output:** Multipart form-data with ZIP file
```
POST /upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="repository.zip"
Content-Type: application/zip

<binary ZIP content>
------WebKitFormBoundary--
```

---

## 🔐 Authentication Matrix

| Auth Type | Configuration | Headers Generated | Use Case |
|-----------|--------------|-------------------|----------|
| **None** | `"auth": null` | None | Public endpoints |
| **Bearer** | `{"type": "bearer", "token_env": "TOKEN"}` | `Authorization: Bearer <token>` | Simple token auth |
| **API Key** | `{"type": "api_key", "key_env": "KEY"}` | `X-API-Key: <key>` | API key services |
| **OAuth2** | `{"type": "oauth2", "token_url": "...", ...}` | `Authorization: Bearer <access_token>` | Enterprise services |

---

## 🔄 Transform Matrix

| Transform Type | Configuration | Input → Output | Use Case |
|---------------|--------------|----------------|----------|
| **None** | `"transform": null` | Direct pass-through | No transformation needed |
| **Named** | `"transform": "qpu_clouditor"` | Calls `_transform_qpu_clouditor()` | Predefined transformers |
| **Custom Mapping** | `"transform": {"field": "${variable}"}` | Variable substitution | Custom field mapping |

### Custom Mapping Variables:

| Variable | Source | Example Value |
|----------|--------|---------------|
| `${toe_id}` | `thing.attributes.toe_id` | `"test-001"` |
| `${repo_name}` | `thing.attributes.repo_name` | `"ai-model"` |
| `${github}` | `thing.attributes.github` | `"https://github.com/..."` |
| `${clone_timestamp}` | `thing.attributes.clone_timestamp` | `"2025-10-10T10:00:00Z"` |
| `${category}` | `thing.attributes.category` | `"AI"` |
| `${sourceType}` | `thing.attributes.sourceType` | `"Repository"` |
| `${files}` | Prepared evidence files | `[{...}, {...}]` |

---

## 📝 Real-World Collector Examples

### Example 1: AI Shield Repository Scanner
```json
{
  "collector_id": "aishield",
  "enabled": true,
  "categories": ["AI"],
  "mqtt": {
    "topics": ["ditto-cobalt/+/+/things/twin/events/created"],
    "filters": {
      "sourceType": ["Repository"]
    }
  },
  "endpoint": "http://localhost:8002/upload/ai",
  "evidence": {
    "type": "zip",
    "include": ["*.py", "*.h5", "*.ipynb", "*.txt", "*.md"],
    "exclude": [".git/*", "__pycache__/*", "*.pyc", "node_modules/*"]
  }
}
```

**Combination:** #19 (zip + None auth + None transform)
**Flow:**
1. AI thing created with Repository sourceType
2. Repository files packaged into ZIP
3. ZIP sent to AIShield endpoint
4. No authentication required
5. No transformation applied

---

### Example 2: SPECTRA ML File Analyzer
```json
{
  "collector_id": "spectra",
  "enabled": true,
  "categories": ["AI"],
  "mqtt": {
    "filters": {
      "file_extensions": [".csv", ".pkl", ".h5"]
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
```

**Combination:** #16 (files + Bearer + Custom mapping)
**Flow:**
1. AI thing created with required files
2. Specific files extracted (dataset.csv, model.pkl)
3. Custom transform applied with variable substitution
4. Bearer token added to headers
5. Transformed JSON sent to SPECTRA

**Output:**
```json
{
  "toe_id": "test-001",
  "project": "ml-model",
  "timestamp": "2025-10-10T10:00:00Z",
  "files": [
    {"name": "dataset.csv", "content": "...", ...},
    {"name": "model.pkl", "content": "...", ...}
  ]
}
```

---

### Example 3: Clouditor QPU Evidence
```json
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
}
```

**Combination:** #18 (files + OAuth2 + Custom mapping)
**Flow:**
1. QDT thing created
2. qpu_data.json file extracted
3. Custom transform with nested objects
4. OAuth2 token obtained from Clouditor
5. Transformed JSON sent with Bearer token

**Output:**
```json
{
  "id": "qpu-001",
  "timestamp": "2025-10-10T10:00:00Z",
  "toolId": "QPU-Scanner",
  "resource": {
    "id": "qpu-001",
    "type": "QuantumProcessingUnit"
  },
  "qpu_data": {
    "files": [{"name": "qpu_data.json", "content": {...}}]
  }
}
```

---

### Example 4: BOM Analyzer
```json
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
```

**Combination:** #7 (thing with features + API Key + No transform)
**Flow:**
1. BOMS thing created with cyclonedx/spdx sourceType
2. Selected features extracted (components, metadata)
3. API key added to headers
4. Filtered thing JSON sent to BOM Analyzer

**Output:**
```json
{
  "thingId": "cobalt.sdt:toe-123-BOMS-...",
  "attributes": {...},
  "features": {
    "components": {...},
    "metadata": {...}
  }
}
```

---

## 🎯 Quick Reference: What Combination Do I Need?

| Need | Use Evidence Type | Use Auth | Use Transform | Combination # |
|------|------------------|----------|---------------|---------------|
| Send full thing, no security | `thing` | None | None | #1 |
| Send full thing, secured | `thing` | Bearer/API Key | None | #2, #3 |
| Send custom format | `thing` | Any | Custom mapping | #5-#8 |
| Send only some features | `thing` + `include_features` | Any | Any | #9-#10 |
| Send specific files | `files` | Any | Any | #11-#18 |
| Send repository archive | `zip` | Any | None | #19-#22 |
| QPU to Clouditor | `files` | OAuth2 | Custom mapping | #18 |
| AI model to scanner | `zip` | None | None | #19 |
| ML files to analyzer | `files` | Bearer | Custom mapping | #16 |

---

## ✅ Summary

Template 3.0 supports **22 different evidence combinations**, covering all common use cases:

- **8 combinations** for `thing` evidence (full or partial)
- **8 combinations** for `files` evidence (specific files)
- **4 combinations** for `zip` evidence (repository archives)
- **4 authentication types** (None, Bearer, API Key, OAuth2)
- **3 transform types** (None, Named, Custom mapping)

All combinations are **fully implemented and production-ready**! 🚀
