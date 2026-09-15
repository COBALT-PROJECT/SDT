# SDT Changes Log

Date: 2026-07-10
Scope: Make IDS-synced QPU (QDT) evidence reach Clouditor end-to-end via the MQTT + template path, fix the crashes/bugs found along the way, add CORS, and document the service.

---

## 1. Goal / design

Data was sent from **IDS → SDT** via `sync/ids`, but it was **not reaching Clouditor**. The intended design (confirmed during the work):

- **`sync/ids` only ingests + categorizes** — it fetches from the IDS connector, tags each artifact with a category (`QDT` / `AI`), and creates the "thing" in Eclipse Ditto. It does **not** notify Clouditor directly.
- **Notification is triggered by MQTT** — when a thing is created in Ditto, Ditto fires an MQTT change event; the listener (`listen_to_ditto.on_message`) routes it. If a template collector matches (`get_subscribed_collectors`), it uses the **template path** (`send_notification`); otherwise it falls back to the legacy `get_evidence(notify=True)` path.
- The **template** (`templates/template.json`) declares the collector: category filter, mqtt topics, Clouditor endpoint/auth URLs, the evidence file, and the transform.

Working QDT → Clouditor path:
```
sync/ids?category=QDT → thing in Ditto (file at attributes.file_path)
  → Ditto MQTT event → on_message (category=QDT)
  → get_subscribed_collectors matches (topic ditto-cobalt/*, category QDT)
  → send_notification:
       _get_files → reads qpu_data.json from attributes.file_path
       _transform_payload("qpu_data") → _transform_qpu_data → Clouditor evidence
       token @ CLOUDITOR_AUTH_PORT (8080)  →  POST evidence @ CLOUDITOR_PORT (8083)
```

---

## 2. Changes by file (all pending, uncommitted)

### `core/config.py`
- `Clouditor_IP = os.getenv("CLOUDITOR_IP") or os.getenv("CLOUDITOR_HOST")` — the deployment sets `CLOUDITOR_IP`, but the code previously only read `CLOUDITOR_HOST`, so the host resolved to `None` (`host='none'` DNS errors).
- `Clouditor_PORT` default changed `8080 → 8083` (assessment/evidence REST port).
- **Added** `Clouditor_AUTH_PORT = os.getenv("CLOUDITOR_AUTH_PORT", "8080")` (OAuth2 token REST port). Clouditor serves auth and assessment on **separate ports**.

### `core/translator.py` — caller-supplied category (fixes crash)
- `process_ids_response(..., category=None)`, `_process_resource_directly(..., category=None)`, and `_create_thing_from_metadata(..., category=None)` all now take `category`, threaded through every call site.
- **Why:** the category-resolution block lived in `_create_thing_from_metadata` but that method didn't receive `category`, and referenced it before assignment → `UnboundLocalError` / `NameError: name 'category' is not defined`, swallowed by `try/except` → `Processed 0 things from IDS connector`. Threading the parameter through fixes it; synced files now become things tagged with the correct category.

### `core/controller.py`
- **`sync_ids_connector(..., category=None)`** — accepts a category and passes it to the translator (`process_ids_response(..., category=category)`).
- **Removed** the direct `notification_push_QDT` push loop from `sync_ids_connector` — sync is ingestion-only; notification happens via MQTT (removes the double-send).
- **`on_message` guard** — skip events for things with no category (parent-thing updates aren't evidence). Prevents the downstream `None` crash.
- **`get_evidence` guard** — if `process_query` returns `None`, log and return instead of dereferencing → fixes `AttributeError: 'NoneType' object has no attribute 'get'`.

### `core/evidence_provider.py`
- **`current_usecase`** — initialized in `__init__` and set whenever a template loads. `send_notification` used `self.current_usecase` which was never set → `AttributeError` on its first line, so the whole template path crashed before sending. **This was the main blocker for the MQTT/template QDT path.**
- **`_get_files`** — now resolves the file from `attributes.file_path` / `attributes.filename` (IDS single-file things) in addition to `Repository_file_tree` (GitHub things). IDS-synced files are now locatable by the template path.
- **`_transform_qpu_data`** — computes `data_dict` (dict-guard) **before** reading `qpu_id`, so an array `qpu_data.json` no longer throws `AttributeError` (previously swallowed → untransformed data sent).
- **`notification_push_QDT`** (legacy path) — token URL now uses `Clouditor_AUTH_PORT` (8080) while the evidence URL keeps `Clouditor_PORT` (8083). Previously used one port for both → token call hit the evidence port and failed. (`Clouditor_AUTH_PORT` added to the import.)

### `core/unified_file_extractor.py`
- Added `_extract_json_file(self, payload, metadata)` wired into the three `json_file` branches of `extract_file_from_json` — handles base64-encoded and plain JSON, returns UTF-8 bytes.
- Hardened base64 handling: `import binascii`; invalid base64 returns `(None, None, None)` instead of raising; the non-UTF-8 fallback decodes with `errors='replace'` (no double-throw).

### `sdt_interface-3.py`
- `GET /api/SDT/sync/ids` accepts `category` (default `"QDT"`), passed to `sync_ids_connector`.
- **CORS**: added `CORSMiddleware` with allowlist `["http://10.163.1.102"]`, registered **after** the auth middleware so CORS sits outermost and answers preflight `OPTIONS` before the token check.

### `templates/template.json` (the file the runtime loads at startup)
- Now the **Quantum/Clouditor** collector config: category `QDT`, oauth2 auth, `transform: qpu_data`, evidence `files: ["qpu_data.json"]`, split ports (`CLOUDITOR_PORT` evidence / `CLOUDITOR_AUTH_PORT` token).
- **Added the `mqtt` block** `{"topics": ["ditto-cobalt/*"]}`. Without it, `_setup_mqtt_subscriptions` uses the default `ditto-cobalt/+/...` pattern, which `_topic_matches` (fnmatch) can't match (`+` is literal) → the collector never matches → falls back to the legacy path. `*` matches; the category filter does the narrowing.

### `templates/Quantum usecase/template.json`
- Removed the trailing comma (invalid JSON that blocked template loading), added the `mqtt` block, set `transform: qpu_data`, and split the ports (auth port for `token_url`). Kept in sync with `templates/template.json`.

### `CLAUDE.md` (new)
- Project guide: run/test/build commands, the k3s build→import→restart deploy cycle, architecture (Controller/Translator/EvidenceProvider/Adapter + Ditto + MQTT), Template 3.0, env vars, Clouditor split-port caveat.

### `SDT-Manager/yaml_scripts/sdt-pod-with-ditto-k3s-itr2.yaml` (deployment, separate path)
- `CLOUDITOR_PORT: "9090" → "8083"` (9090 was gRPC), **added** `CLOUDITOR_AUTH_PORT: "8080"` and `CLOUDITOR_SECRET: "clouditor"` (the template's oauth2 returns empty headers if the secret is unset).

---

## 3. Clouditor connectivity — verified

- **Ports/IPs correct:** token `10.163.1.127:8080/v1/auth/token` → 200 (valid JWT, `sub=clouditor`); evidence `10.163.1.127:8083/v1/assessment/evidences` → 401 without token (live, needs auth). Ports `9090/9093` are gRPC (not for the HTTP client).
- On 2026-06-18 the full flow returned `200 ASSESSMENT_STATUS_ASSESSED`.
- **Current external blocker (not SDT):** the evidence POST now returns `500 "could not retrieve metric list from orchestrator: Unauthenticated"` — a **Clouditor-internal** inter-service auth problem (assessment → orchestrator). SDT's token is valid and reaches the right endpoint; this must be fixed on the Clouditor deployment.

---

## 4. Runtime notes / follow-ups

1. **MQTT topic match** — `ditto-cobalt/*` assumes `msg.topic` starts with `ditto-cobalt/`. If the Ditto connection publishes a different prefix, change the template topic to `"*"` (category filter still narrows).
2. **Which template is active** — the runtime loads `templates/template.json` only. `upload-template` overwrites it. `templates/Quantum usecase/template.json` is a reference copy kept in sync.
3. **Clouditor orchestrator 500** — external; see §3.
4. **AI category** — not wired to Clouditor; the legacy `notification_push_AI` posts to a dummy `localhost:8002` URL. Inert (won't disrupt SDT), but AI artifacts don't reach Clouditor by design.

---

## 5. Deploy (image pinned to `0.2.8`; pod does not auto-pull)

```bash
docker build -t arq101/sdt-main-image:0.2.8 -t sdt-main-image:0.2.8 .
docker save arq101/sdt-main-image:0.2.8 > /tmp/sdt-image.tar
sudo k3s ctr images import /tmp/sdt-image.tar
kubectl apply -f ../SDT-Manager/yaml_scripts/sdt-pod-with-ditto-k3s-itr2.yaml   # new env vars
kubectl rollout restart deployment/sdt-deployment -n default
```
