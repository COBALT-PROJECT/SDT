# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The Security Digital Twin (SDT) Service — a FastAPI middleware that ingests security evidence (CycloneDX/SBOM, OSCAL, ARM, Quantum/QPU data, GitHub repos, IDS-connector artifacts), stores each as a "thing" in an **Eclipse Ditto** digital twin, and forwards/transforms that evidence to external collectors (Clouditor, Watchtower, etc.) via Template 3.0 configs.

This `SDT/` directory is one component of the larger `SDTM/` system (siblings: `ditto/`, `IDS-Connector/`, `SDT-Manager/`, `IdentityManagement/`, `true-connector/`). SDT talks to those over the network, not via shared code.

## Commands

```bash
# Run locally — note the hyphenated module name and required PYTHONPATH
export PYTHONPATH=$PWD
uvicorn sdt_interface-3:app --host 0.0.0.0 --port 8000

# Tests (CI runs exactly this)
export PYTHONPATH=$PYTHONPATH:$PWD
pytest tests/test_core.py -v --cov=core

# Single test
pytest tests/test_core.py::<test_name> -v

# Lint (pre-commit: trailing-whitespace + end-of-file-fixer only)
pre-commit run --all-files
```

### Build & deploy to k3s

The running system is a k3s pod (`sdt-deployment` in namespace `default`), exposed via NodePort **30008 → 8000** (API) and **30009 → 1883** (MQTT). The deployment manifest lives outside this repo at `../SDT-Manager/yaml_scripts/sdt-pod-with-ditto-k3s-itr2.yaml`.

The image tag is **pinned to `0.2.8`** (CI in `.github/workflows/main.yml` builds/pushes the same tag). To deploy local changes, rebuild that tag, import into k3s containerd, and restart — the pod does NOT auto-pull:

```bash
docker build -t arq101/sdt-main-image:0.2.8 -t sdt-main-image:0.2.8 .
docker save arq101/sdt-main-image:0.2.8 > /tmp/sdt-image.tar
sudo k3s ctr images import /tmp/sdt-image.tar          # k3s uses its own containerd store
kubectl rollout restart deployment/sdt-deployment -n default
```

A `kubectl exec` + `PYTHONPATH=/app python3 -c "..."` into the pod is the fastest way to test a single method (e.g. an evidence push) against the live Ditto/Clouditor without a full request cycle.

## Architecture

`sdt_interface-3.py` is the FastAPI app and the only entrypoint. It instantiates a single global `Controller` (`ctrl`) and wires a Bearer-token middleware over every route except auth/health/sync. The four core classes:

- **`core/controller.py` (`Controller`)** — the orchestrator. Owns Ditto CRUD (things + a per-TOE "parent thing" that indexes children), the MQTT/Ditto listener, IDS-connector sync, and holds references to the other three components (`self.trs`, `self.ep`, adapter). Almost every endpoint delegates here.
- **`core/translator.py` (`Translator`)** — converts inbound external data (notably IDS-connector responses with multiply-escaped embedded files) into Ditto thing JSON. Writes extracted file bytes to `evidence/` and records the path in `attributes.file_path` + `features.file_metadata`.
- **`core/evidence_provider.py` (`EvidenceProvider`)** — the outbound side. Loads Template 3.0 configs, matches things to collectors by category, prepares/transforms payloads, and POSTs to collectors. Contains the QPU→Clouditor path (`notification_push_QDT`, `_transform_qpu_data`).
- **`core/adapter_all.py` (`DTModelAdapter`)** — CycloneDX/OSCAL/ARM → Ditto model mapping.

### Data flow (two directions)
- **Inbound:** external source → endpoint/sync → `Translator` builds thing → `Controller.create_in_ditto` (creates policy from `core/Policies/policy.json`, the thing, and updates the parent thing).
- **Outbound:** thing in Ditto → `EvidenceProvider` matches a collector via template category → transform → POST to collector. This can be triggered by the MQTT/Ditto listener or directly after a sync.

### Identity scheme in Ditto
Things are `cobalt.sdt:toe-<toe_id>-<category>-<timestamp>-<rand>`; the index is `cobalt.sdt:parent-<toe_id>`. Categories (`AI`, `QDT`, `BOMS`, `OSCAL`, `ARM`, `FILE`, …) drive both ID naming and which template collector handles a thing.

## Templates (3.0)

Evidence routing is config-driven by `templates/<usecase>/template.json` (and a default `templates/template.json`). Each `evidence_collectors[]` entry declares `categories`, an `endpoint`, `auth` block, an `evidence` spec (`thing`/`files`/`zip`), and an optional named `transform` (e.g. `qpu_clouditor` → `_transform_qpu_data`). `${VAR}` tokens in endpoints/auth are substituted from env at send time.

These files are **strict JSON** — a trailing comma silently breaks template loading (`EvidenceProvider` logs `Error loading template: Expecting value...` and then matches no collectors, so nothing is ever sent). Validate after editing.

## Configuration (env vars, read in `core/config.py`)

| Var | Purpose | Notes |
|-----|---------|-------|
| `DITTO_HOST` / `DITTO_PORT` | Eclipse Ditto API | `ditto:80` in-cluster |
| `MQTT_BROKER_HOST` / `_PORT` | MQTT for Ditto change events | mosquitto runs inside the same container (started by `start.sh`) |
| `CLOUDITOR_IP` (or legacy `CLOUDITOR_HOST`) | Clouditor host | |
| `CLOUDITOR_PORT` | Clouditor port | **Caveat:** Clouditor splits services across ports — OAuth2 token on one (observed `8080`), assessment/evidence on another (observed `8083`). A single `CLOUDITOR_PORT` cannot serve both; the evidence push needs the token from the auth port and the POST to the evidence port. |
| `IDS_CONNECTOR_HOST` / `_PORT` | IDS connector sync source | |

The container entrypoint (`Dockerfile` → `/app/start.sh`) starts mosquitto in the background then runs uvicorn; `PYTHONPATH=/app` and `WORKDIR=/app/SDT` are set there.

## Auth model

SDT-Manager distributes an OAuth2 Bearer token to SDT via `POST /api/SDT/auth/token`; the middleware then requires it on protected routes. `/api/SDT/sync/ids`, `/auth/*`, and `/health` are exempt (see the exempt list in `sdt_interface-3.py`).
