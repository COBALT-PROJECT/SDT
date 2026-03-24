# SDT API — Workflow Scenario

Overview
--------
This document describes a typical end-to-end workflow using the SDT HTTP API: create → sync → parent → children → evidence → another sync → read → update → delete. Use the examples below to exercise and validate the service behavior (Ditto, MQTT broker and IDS connector must be available).

Prerequisites
-------------
- SDT service running (default: `http://{SDT IP}:38000`).
- Eclipse Ditto reachable (configured via `DITTO_HOST`/`DITTO_PORT`).
- MQTT broker available (configured via `MQTT_BROKER_HOST`).
- IDS Connector reachable (`IDS_CONNECTOR_HOST`/`IDS_CONNECTOR_PORT`).
- Sample payloads in repo: `test_workflow_data.json`, `test_ids_data.json`.

Quick sequence
--------------
1. create — push a Thing into Ditto (optionally create parent)
2. sync (IDS) — fetch artifacts from IDS Connector into SDT
3. parent.create — explicitly create a parent thing (if needed)
4. parent.children — list child things under parent
5. evidence — request/download evidence for a thing
6. sync (IDS) again — pick up updates
7. read — inspect stored thing
8. update — change thing content or metadata
9. delete — remove a thing (updates parent)

Example: step-by-step (curl)
----------------------------
Replace TOE ID below with your UUID (examples use zeros):

1) Create (push Thing into SDT)

```bash
curl -s -X POST "http://{SDT IP}:38000/api/SDT/create/?toeid=00000000-0000-0000-0000-000000000000&payload_type=BOMS&create_genesis=true" \
  -H 'Content-Type: application/json' \
  -d @test_workflow_data.json
```
- Expected: JSON success + creation details. If `create_genesis=true` the genesis thing is created/updated.

2) Sync from IDS connector (ingest external resources)

```bash
curl -s "http://{SDT IP}:38000/api/SDT/sync/ids?data_path=all&toeid=00000000-0000-0000-0000-000000000000"
```
- Expected: list of artifacts processed/created in Ditto.

3) Create genesis explicitly (optional)

```bash
curl -s -X POST "http://{SDT IP}:38000/api/SDT/genesis/create?toeid=00000000-0000-0000-0000-000000000000" \
  -H 'Content-Type: application/json' \
  -d '{"owner":"team-x","env":"dev"}'
```
- Expected: `201` if newly created, `200` if it already existed.

4) List genesis children

```bash
curl -s "http://{SDT IP}:38000/api/SDT/genesis/children?toeid=00000000-0000-0000-0000-000000000000"
```
- Expected: JSON object mapping child thing IDs → metadata (type, timestamps).

5) Retrieve evidence (JSON or download)

- JSON metadata
```bash
curl -s "http://{SDT IP}:38000/api/SDT/evidence/?toeid=00000000-0000-0000-0000-000000000000&category=AI&format=json"
```
- Download ZIP
```bash
curl -s -o evidence.zip "http://{SDT IP}:38000/api/SDT/evidence/?toeid=00000000-0000-0000-0000-000000000000&category=AI&evidence_type=zip&format=download"
```
- Use `transform=` param (e.g. `transform=qpu_clouditor`) to request transformed payloads.


Evidence endpoint — extraction details
--------------------------------------
The `/api/SDT/evidence/` endpoint supports `evidence_type=thing|zip|files|specific|auto` and adapts its output depending on the Thing `sourceType` or on the file type that was ingested (via `/api/SDT/sync/ids` or `/api/SDT/create`). Below are the common inputs and what the endpoint can extract and return.

Supported extraction (by incoming artifact type)
- CycloneDX (SBOM/BOM)
  - Extracted: `metadata`, `components`, `services`, `dependencies`, `vulnerabilities`, relationships.
  - Use: `include_features=components` or `format=json` to return full Thing/CycloneDX structure.

- OSCAL component definitions
  - Extracted: component `metadata`, `components`, `capabilities`, `back-matter` (full OSCAL JSON available).

- ARM templates
  - Extracted: `resources`, `parameters`, `outputs` and inferred resource relationships.

- Git repositories (cloned or repository Things)
  - Extracted: `Repository_file_tree` with per-file `path`, `size`, `hash` (sha256), `last_commit`, `mtime`.
  - Use: `evidence_type=zip` + `include_patterns` / `exclude_patterns` or `evidence_type=files` + `files=` to return selected files.

- Jupyter notebooks (`.ipynb`), Python scripts (`.py`), model binaries (`.h5`, `.pt`, etc.)
  - Extracted: file `content` (downloadable), `lines_of_code`, `hash`, `mime_type`.
  - Large binaries are returned via `files` or `zip` (subject to configured max-size limits).

- Generic files (FILE category)
  - Extracted: file bytes + metadata; searchable by `filename` query param.

Parameters & transform support
- `include_patterns` / `exclude_patterns` — glob-like lists for ZIP creation (comma-separated).
- `files` — comma-separated filenames for `evidence_type=files` or `specific`.
- `include_features` — comma-separated Thing features to include (e.g. `components,Repository_file_tree`).
- `filename` — filter when category is `FILE`.
- `transform` — named transform (e.g. `qpu_clouditor`) or inline JSON mapping to reshape output.
- `format` — `json` (metadata) or `download` (FileResponse/ZIP).
- `evidence_type=auto` selects the most useful representation based on Thing `sourceType`.

Example usages
- Request only components from an SBOM: `?toeid=...&category=BOMS&include_features=components&format=json`
- Download `.py` and `.ipynb` files from a repo, excluding `.git`: `?toeid=...&category=REPO&evidence_type=zip&include_patterns=*.py,*.ipynb&exclude_patterns=.git/*&format=download`
- Get specific files from a Thing: `?toeid=...&category=AI&evidence_type=files&files=model.h5,config.json`
- Retrieve a single FILE by filename: `?toeid=...&category=FILE&filename=weights.h5&format=download`
- Apply a named transform: `?toeid=...&category=QDT&transform=qpu_clouditor`

Typical metadata returned
- `name` / `filename`, `size` (bytes), `hash` (sha256), `mime_type`, `lines_of_code`, `last_commit` / `commit_hash`, `timestamp`, `path`.

Notes
- The EvidenceProvider enforces default limits (e.g. max zip file size); very large binaries may be provided only via `files`/`download`.
- Transforms and template-driven mappings live under `SDT/templates/template.json` and can be extended per use case.

6) Repeat IDS sync (pick up new/updated external resources)

```bash
curl -s "http://{SDT IP}:38000/api/SDT/sync/ids?data_path=all&toeid=00000000-0000-0000-0000-000000000000"
```
- Expected: newly ingested/updated things + genesis updated with sync metadata.

7) Read stored thing

```bash
curl -s "http://{SDT IP}:38000/api/SDT/read/?toeid=00000000-0000-0000-0000-000000000000&category=AI"
```
- Expected: the thing JSON returned from Ditto (or `404`/empty when not found).

8) Update a thing

```bash
curl -s -X PUT "http://{SDT IP}:38000/api/SDT/update/?toeid=00000000-0000-0000-0000-000000000000&category=AI" \
  -H 'Content-Type: application/json' \
  -d '{"attributes":{"description":"updated description"}}'
```
- Expected: controller response indicating update success.

9) Delete a thing

```bash
curl -s -X DELETE "http://{SDT IP}:38000/api/SDT/delete/?toeid=00000000-0000-0000-0000-000000000000&category=AI"
```
- Expected: deletion confirmation; genesis is updated to remove reference to the child thing.

Health & debug
--------------
- Service health: `GET /api/SDT/health`
- If Ditto listener is required, the server starts `ctrl.run_ditto_listener()` on import — verify the background listener in logs.

Files & samples
---------------
- API implementation: `sdt_interface-2.py`
- Controller / business logic: `core/controller.py`
- Adapter client example: `core/adapter_all.py`
- Examples to POST: `test_workflow_data.json`, `test_ids_data.json`

Troubleshooting notes
---------------------
- If a `create` returns 201 but the thing is not in Ditto, check Ditto connectivity and controller logs.
- If `evidence` download returns 404, verify the requested `category`/`filename` and that child things exist under genesis.
- For multi-worker deployments, note `ctrl.run_ditto_listener()` runs at import time — you may see duplicate listeners.

Tips & next steps
-----------------
- Use `create` with `create_genesis=true` to keep genesis lifecycle automatic.
- Use `sync/ids` for bulk ingestion from an external IDS connector (use `data_path` to restrict scope).
- To automate tests, script the above `curl` sequence and assert expected responses.

---
If you want, I can also add a runnable example script that executes this entire workflow end-to-end using `curl` or Python. ✅