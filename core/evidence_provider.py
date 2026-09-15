
import logging
import requests
from core.util import FileUtils
from core.config import (
    Clouditor_IP, Clouditor_PORT,
    IAM_TOKEN_URL, IAM_CLIENT_ID, IAM_CLIENT_SECRET, IAM_SCOPE,
)
import os
import json
import uuid
import base64
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class EvidenceProvider():
    def __init__(self, controller=None, template_dir="templates"):
        print(f"SDT-EvidenceProvider instance created")
        self.controller = controller
        self.template_dir = template_dir
        self.usecase_templates = {}
        self.current_usecase = None  # Name of the currently loaded use case template
        self.mqtt_subscriptions = {}  # Track MQTT subscriptions
        self._load_usecase_templates()
        self._setup_mqtt_subscriptions()

    def get_subscribed_collectors(self, mqtt_topic: str, thing: dict):
        """
        Get collectors that should be notified based on MQTT topic and thing data
        """
        matching_collectors = []

        for collector_name, subscription in self.mqtt_subscriptions.items():
            # Check if topic matches
            if not self._topic_matches(mqtt_topic, subscription["topics"]):
                continue

            # Check if thing matches filters
            if not self._thing_matches_filters(thing, subscription["filters"]):
                continue

            matching_collectors.append(subscription["collector"])

        return matching_collectors

    def _topic_matches(self, mqtt_topic: str, topic_patterns: list):
        """Check if MQTT topic matches any pattern"""
        import fnmatch

        for pattern in topic_patterns:
            if fnmatch.fnmatch(mqtt_topic, pattern):
                return True
        return False

    def _thing_matches_filters(self, thing: dict, filters: dict):
        """Check if thing matches filter criteria"""
        attributes = thing.get("attributes", {})

        # Check category filter
        categories = filters.get("category", [])
        if categories and attributes.get("category") not in categories:
            return False

        # Check sourceType filter
        source_types = filters.get("sourceType", [])
        if source_types and attributes.get("sourceType") not in source_types:
            return False

        # Check file extensions (for file-based evidence)
        file_extensions = filters.get("file_extensions", [])
        if file_extensions:
            # Check Repository_file_tree for matching extensions
            file_tree = thing.get("features", {}).get("Repository_file_tree", {}).get("properties", {})
            has_matching_file = any(
                any(file_info.get("name", "").endswith(ext) for ext in file_extensions)
                for file_info in file_tree.values()
            )
            if not has_matching_file:
                return False

        # Exclude deleted events
        if filters.get("exclude_deleted", True):
            topic = thing.get("topic", "")
            if "/deleted" in topic:
                return False

        return True





    def _prepare_zip_evidence(self, thing: dict, evidence_format: dict):
        """Create ZIP archive based on file patterns"""
        import fnmatch
        import zipfile
        import tempfile

        repo_path = thing.get("attributes", {}).get("github")
        include_config = evidence_format.get("include_files", {})

        patterns = include_config.get("patterns", [])
        exclude_patterns = include_config.get("exclude_patterns", [])
        max_size_mb = include_config.get("max_file_size_mb", 100)

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"{thing.get('thingId')}.zip")

        # Create ZIP with filtered files
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(repo_path):
                # Filter by patterns
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Check if matches include patterns
                    if not any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                        continue

                    # Check if matches exclude patterns
                    if any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns):
                        continue

                    # Check file size
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if file_size_mb > max_size_mb:
                        logger.warning(f"Skipping large file: {rel_path} ({file_size_mb:.2f} MB)")
                        continue

                    zipf.write(file_path, rel_path)

        return {"file": open(zip_path, "rb")}

    def _prepare_file_evidence(self, thing: dict, evidence_format: dict):
        """Prepare specific files"""
        include_config = evidence_format.get("include_files", {})
        specific_names = include_config.get("specific_names", [])

        # Find files in file tree
        file_tree = thing.get("features", {}).get("Repository_file_tree", {}).get("properties", {})

        files_to_send = []
        for file_info in file_tree.values():
            if file_info.get("name") in specific_names:
                file_path = file_info.get("path")
                if os.path.exists(file_path):
                    files_to_send.append({
                        "name": file_info.get("name"),
                        "path": file_path,
                        "hash": file_info.get("hash"),
                        "size": os.path.getsize(file_path)
                    })

        return files_to_send

    def _prepare_json_evidence(self, thing: dict, evidence_format: dict):
        """Prepare JSON evidence"""
        include_attrs = evidence_format.get("include_thing_attributes", [])
        include_features = evidence_format.get("include_thing_features", [])

        evidence = {}

        # Include specified attributes
        for attr in include_attrs:
            if attr in thing.get("attributes", {}):
                evidence[attr] = thing["attributes"][attr]

        # Include specified features
        for feature in include_features:
            if feature in thing.get("features", {}):
                evidence[feature] = thing["features"][feature]

        return evidence


    def _apply_custom_mapping(self, thing: dict, evidence_data: dict, mapping: dict):
        """Apply custom field mapping with variable substitution"""
        result = {}

        for key, value in mapping.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Variable substitution
                path = value[2:-1]  # Remove ${ and }
                result[key] = self._extract_value_by_path(thing, path)
            elif isinstance(value, dict):
                result[key] = self._apply_custom_mapping(thing, evidence_data, value)
            else:
                result[key] = value

        return result

    def _extract_value_by_path(self, obj: dict, path: str):
        """Extract value from nested dict using dot notation"""
        parts = path.split(".")
        current = obj

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

        return current

    def _get_authentication_headers(self, auth_config: dict):
        """Generate authentication headers based on configuration"""
        auth_type = auth_config.get("type", "none")

        if auth_type == "none":
            return {}

        elif auth_type == "bearer":
            token_env = auth_config.get("token_env_var")
            token = os.getenv(token_env)
            return {"Authorization": f"Bearer {token}"}

        elif auth_type == "api_key":
            header_name = auth_config.get("header_name", "X-API-Key")
            key_env = auth_config.get("key_env_var")
            key = os.getenv(key_env)
            return {header_name: key}

        elif auth_type == "oauth2_client_credentials":
            token_endpoint = self._substitute_env_vars(auth_config.get("token_endpoint"))
            client_id = auth_config.get("client_id")
            client_secret_env = auth_config.get("client_secret_env_var")
            client_secret = os.getenv(client_secret_env)

            # Get token
            import base64
            basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

            token_resp = requests.post(
                token_endpoint,
                headers={
                    "Authorization": f"Basic {basic_auth}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={"grant_type": "client_credentials"}
            )

            access_token = token_resp.json().get("access_token")
            return {"Authorization": f"Bearer {access_token}"}

        return {}

    def _substitute_env_vars(self, text: str):
        """Substitute environment variables in text"""
        if not text:
            return text

        import re
        pattern = r'\$\{([^}]+)\}'

        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))

        return re.sub(pattern, replace_var, text)

    def _retry_notification(self, collector: dict, thing: dict, retry_config: dict):
        """Retry failed notifications"""
        max_attempts = retry_config.get("max_attempts", 3)
        backoff_seconds = retry_config.get("backoff_seconds", 5)

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Retry attempt {attempt}/{max_attempts}")
            time.sleep(backoff_seconds * attempt)

            try:
                result = self.send_notification(collector, thing)
                if result and 200 <= result < 300:
                    return result
            except Exception as e:
                logger.error(f"Retry attempt {attempt} failed: {e}")

        return None


    def _setup_mqtt_subscriptions(self):
        """Setup MQTT subscriptions (simplified)"""
        for usecase_name, usecase_data in self.usecase_templates.items():
            collectors = usecase_data.get("evidence_collectors", [])

            for collector in collectors:
                if not collector.get("enabled", True):
                    continue

                collector_id = collector.get("collector_id")
                categories = collector.get("categories", [])

                # Default topics if not specified
                mqtt_config = collector.get("mqtt", {})
                topics = mqtt_config.get("topics", ["ditto-cobalt/+/+/things/twin/events/+"])
                filters = mqtt_config.get("filters", {})
                filters["category"] = categories  # Always filter by category

                self.mqtt_subscriptions[collector_id] = {
                    "topics": topics,
                    "filters": filters,
                    "collector": collector
                }

    def send_notification(self, collector: dict, thing: dict):
        """Send notification (simplified)"""
        # Get defaults
        defaults = self.usecase_templates.get(self.current_usecase, {}).get("defaults", {})

        try:
            # Prepare evidence
            evidence_config = collector.get("evidence", {})
            evidence_data = self._prepare_evidence(thing, evidence_config)

            # Transform if needed
            transform_config = collector.get("transform")
            if transform_config:
                payload = self._transform_payload(thing, evidence_data, transform_config)
            else:
                payload = evidence_data

            # Get auth headers
            auth_config = collector.get("auth")
            headers = self._get_auth_headers(auth_config) if auth_config else {}

            # Auto-detect Content-Type
            evidence_type = evidence_config.get("type", "thing")
            if evidence_type == "zip":
                # Will be multipart/form-data
                response = requests.post(
                    self._substitute_env(collector.get("endpoint")),
                    files=payload,
                    headers=headers,
                    timeout=defaults.get("timeout_seconds", 30)
                )
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(
                    self._substitute_env(collector.get("endpoint")),
                    json=payload,
                    headers=headers,
                    timeout=defaults.get("timeout_seconds", 30)
                )

            logger.info(f"Notification sent to {collector.get('collector_id')}, status: {response.status_code}")

            # Auto-retry on failure
            if response.status_code >= 400:
                self._auto_retry(collector, thing, defaults.get("retry_attempts", 3))

            return response.status_code

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return None

    def _prepare_evidence(self, thing: dict, evidence_config: dict):
        """Prepare evidence (simplified)"""
        evidence_type = evidence_config.get("type", "thing")

        if evidence_type == "thing":
            # Include only specified features if given
            include_features = evidence_config.get("include_features")
            if include_features:
                return {
                    "thingId": thing.get("thingId"),
                    "attributes": thing.get("attributes", {}),
                    "features": {k: v for k, v in thing.get("features", {}).items() if k in include_features}
                }
            return thing

        elif evidence_type == "zip":
            return self._create_zip(thing, evidence_config)

        elif evidence_type == "files":
            return self._get_files(thing, evidence_config)

        return thing

    def _transform_payload(self, thing: dict, evidence_data: dict, transform_config):
        """Transform payload (simplified)"""
        if isinstance(transform_config, str):
            # Named transformer
            transformer_func = getattr(self, f"_transform_{transform_config}", None)
            if transformer_func:
                return transformer_func(evidence_data, thing.get("attributes", {}).get("toe_id"))
            return evidence_data

        elif isinstance(transform_config, dict):
            # Field mapping with variable substitution
            return self._apply_mapping(thing, transform_config)

        return evidence_data

    def _apply_mapping(self, thing: dict, mapping: dict):
        """Apply field mapping with ${variable} substitution"""
        result = {}
        attributes = thing.get("attributes", {})

        for key, value in mapping.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]  # Extract variable name
                result[key] = attributes.get(var_name)
            else:
                result[key] = value

        return result

    def _create_zip(self, thing: dict, evidence_config: dict):
        """Create ZIP archive based on file patterns"""
        import fnmatch
        import zipfile
        import tempfile

        # Get repository path from thing attributes
        repo_path = thing.get("attributes", {}).get("github")
        if not repo_path or not os.path.exists(repo_path):
            logger.error(f"Repository path not found or doesn't exist: {repo_path}")
            return None

        include_patterns = evidence_config.get("include", ["*"])
        exclude_patterns = evidence_config.get("exclude", [])

        # Get defaults
        defaults = {}
        for usecase_data in self.usecase_templates.values():
            if "defaults" in usecase_data:
                defaults = usecase_data["defaults"]
                break

        max_size_mb = defaults.get("max_file_size_mb", 100)

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        thing_id = thing.get("thingId", "unknown").replace(":", "_")
        zip_path = os.path.join(temp_dir, f"{thing_id}.zip")

        # Create ZIP with filtered files
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Check if matches include patterns
                    matches_include = any(fnmatch.fnmatch(file, pattern) for pattern in include_patterns)
                    if not matches_include:
                        continue

                    # Check if matches exclude patterns
                    matches_exclude = any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns)
                    if matches_exclude:
                        continue

                    # Check file size
                    try:
                        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        if file_size_mb > max_size_mb:
                            logger.warning(f"Skipping large file: {rel_path} ({file_size_mb:.2f} MB)")
                            continue

                        zipf.write(file_path, rel_path)
                    except Exception as e:
                        logger.error(f"Error adding file to ZIP: {file_path}, error: {e}")

        return {"file": (os.path.basename(zip_path), open(zip_path, "rb"), "application/zip")}

    def _get_files(self, thing: dict, evidence_config: dict):
        """Get specific files from thing.

        Resolves each requested file from the Repository_file_tree feature (GitHub-style
        things) or, failing that, from the thing's own metadata (attributes.file_path /
        filename) used by IDS-synced single-file things.
        """
        files_list = evidence_config.get("files", [])

        file_tree = thing.get("features", {}).get("Repository_file_tree", {}).get("properties", {})
        attributes = thing.get("attributes", {})
        thing_filename = attributes.get("filename")
        thing_file_path = attributes.get("file_path")

        result_files = []
        for file_name in files_list:
            found = False

            # 1) GitHub-style things: look in Repository_file_tree
            for file_key, file_info in file_tree.items():
                if isinstance(file_info, dict) and file_info.get("name") == file_name:
                    file_path = file_info.get("path")
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.read()
                        result_files.append({
                            "name": file_name,
                            "path": file_path,
                            "content": content,
                            "hash": file_info.get("hash"),
                            "size": os.path.getsize(file_path)
                        })
                        found = True
                    break

            # 2) IDS-style single-file things: resolve from thing metadata
            if not found and thing_filename == file_name and thing_file_path and os.path.exists(thing_file_path):
                with open(thing_file_path, 'r') as f:
                    content = f.read()
                result_files.append({
                    "name": file_name,
                    "path": thing_file_path,
                    "content": content,
                    "size": os.path.getsize(thing_file_path)
                })

        return {"files": result_files}

    def _get_auth_headers(self, auth_config: dict):
        """Generate authentication headers based on configuration"""
        if not auth_config:
            return {}

        auth_type = auth_config.get("type", "none")

        if auth_type == "none":
            return {}

        elif auth_type == "bearer":
            token_env = auth_config.get("token_env")
            token = os.getenv(token_env)
            if token:
                return {"Authorization": f"Bearer {token}"}
            else:
                logger.warning(f"Bearer token not found in environment variable: {token_env}")
                return {}

        elif auth_type == "api_key":
            key_env = auth_config.get("key_env")
            key = os.getenv(key_env)
            if key:
                return {"X-API-Key": key}
            else:
                logger.warning(f"API key not found in environment variable: {key_env}")
                return {}

        elif auth_type == "oauth2":
            try:
                token_url = self._substitute_env_vars(auth_config.get("token_url"))
                client_id = auth_config.get("client_id")
                client_secret_env = auth_config.get("client_secret_env")
                client_secret = os.getenv(client_secret_env)

                if not client_secret:
                    logger.warning(f"OAuth2 client secret not found in environment variable: {client_secret_env}")
                    return {}

                # Get token using client credentials
                basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

                token_data = {"grant_type": "client_credentials"}
                scope = auth_config.get("scope")
                if scope:
                    token_data["scope"] = scope

                token_resp = requests.post(
                    token_url,
                    headers={
                        "Authorization": f"Basic {basic_auth}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data=token_data,
                    timeout=10
                )

                if token_resp.status_code == 200:
                    access_token = token_resp.json().get("access_token")
                    return {"Authorization": f"Bearer {access_token}"}
                else:
                    logger.error(f"Failed to get OAuth2 token: {token_resp.status_code}")
                    return {}
            except Exception as e:
                logger.error(f"Error getting OAuth2 token: {e}")
                return {}

        return {}

    def _substitute_env(self, text: str):
        """Substitute environment variables in text (alias for _substitute_env_vars)"""
        return self._substitute_env_vars(text)

    def _auto_retry(self, collector: dict, thing: dict, max_attempts: int):
        """Auto-retry failed notifications"""
        import time

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Retry attempt {attempt}/{max_attempts} for collector {collector.get('collector_id')}")
            time.sleep(5 * attempt)  # Exponential backoff

            try:
                result = self.send_notification(collector, thing)
                if result and 200 <= result < 300:
                    logger.info(f"Retry attempt {attempt} succeeded")
                    return result
            except Exception as e:
                logger.error(f"Retry attempt {attempt} failed: {e}")

        logger.error(f"All retry attempts failed for collector {collector.get('collector_id')}")
        return None

    def _load_usecase_templates(self):
        """Load template file from SDT/templates/template.json."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(current_dir, "..", self.template_dir, "template.json")

            if not os.path.exists(template_path):
                logger.warning(f"Template file not found: {template_path}")
                return

            with open(template_path, 'r') as f:
                template_data = json.load(f)

            # Assuming template_data is a single template dict
            usecase_name = template_data.get("config_name", "default")
            self.usecase_templates[usecase_name] = template_data
            self.current_usecase = usecase_name  # Track the active use case for defaults lookup
            logger.info(f"Loaded template: {usecase_name}")
        except Exception as e:
            logger.error(f"Error loading template: {e}")

    def get_usecase_template(self, usecase: str, level: str):
        """
        Get template for the specified use case and evidence level.
        """
        usecase_data = self.usecase_templates.get(usecase)

        if usecase_data and "evidence_collectors" in usecase_data:
            collectors = usecase_data["evidence_collectors"]

            # Search for collector that handles this level
            for collector_config in collectors:
                categories = collector_config.get("categories", [])
                # Check if this collector handles the requested level
                if level.upper() in [cat.upper() for cat in categories]:
                    if collector_config.get("enabled", True):
                        return collector_config.copy()

        return None

    def process_query(self, toe_id: str, level: str, json_data: dict, usecase: str = None):
        """
        Processes evidence query and returns template for notification
        """
        # Try to load template from use case
        if usecase:
            template = self.get_usecase_template(usecase, level)
            if template:
                return template

        # Fallback to embedded templates if no use case specified
        return self._get_fallback_template(level)

    def _get_fallback_template(self, level: str):
        """
        Returns fallback template for backward compatibility
        """
        # This is for backward compatibility with old code
        # that doesn't use the new template system
        if level and level.upper() == "AI":
            return {
                "evidence_collector": "legacy_ai",
                "evidence_type": "repository",
                "evidence_format": "zip"
            }
        elif level and level.upper() == "QDT":
            return {
                "evidence_collector": "legacy_qdt",
                "evidence_type": "paths",
                "evidence_format": "file-by-file"
            }

        return None

    def notification_push_AI(self, evidence_dir, toe_id):
        """
        Legacy method: Zips the evidence directory and sends it to AI endpoint
        """
        try:
            zip_path, zip_filename = FileUtils.zip_file(evidence_dir, toe_id)

            dummy_url = "http://localhost:8002/upload/ai"

            with open(zip_path, "rb") as f:
                files = {"file": (zip_filename, f, "application/zip")}
                response = requests.post(dummy_url, files=files, timeout=30)
                logger.info(f"AI notification sent, status: {response.status_code}")
                return response.status_code
        except Exception as e:
            logger.error(f"Error sending AI notification: {e}")
            return None

    def _get_iam_token(self):
        """
        Get an OAuth2 access token from the COBALT IAM via client_credentials grant.
        This token is what's sent (as Bearer) to Clouditor's evidence endpoint.
        """
        response = requests.post(
            IAM_TOKEN_URL,
            auth=(IAM_CLIENT_ID, IAM_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials", "scope": IAM_SCOPE},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("access_token")

    def notification_push_QDT(self, file_path, toe_id=None, filename=None):
        """
        Legacy method: Reads QPU data JSON, transforms it, and sends to Clouditor
        """
        try:
            # Read QPU data
            with open(file_path, 'r') as f:
                qpu_data = json.load(f)

            # Get access token from the IAM (client_credentials grant)
            access_token = self._get_iam_token()
            if not access_token:
                logger.error("IAM token response did not contain an access_token")
                return None

            # Transform QPU data
            transformed_data = self._transform_qpu_data(qpu_data, toe_id)

            # Send to Clouditor
            evidence_url = f"http://{Clouditor_IP}:{Clouditor_PORT}/v1/assessment/evidences"
            response = requests.post(
                evidence_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=transformed_data,
                timeout=30
            )

            logger.info(f"QDT notification sent, status: {response.status_code}")
            return response.status_code
        except Exception as e:
            logger.error(f"Error sending QDT notification: {e}")
            return None

    def _transform_qpu_data(self, evidence_data: dict, toe_id: str = None):
        """
        Transform QPU data to Clouditor evidence format
        """
        try:
            # Extract QPU data from files structure
            if isinstance(evidence_data, dict) and "files" in evidence_data:
                # New template system: evidence_data = {"files": [{"name": "qpu_data.json", "content": "..."}]}
                files_list = evidence_data.get("files", [])
                if files_list and len(files_list) > 0:
                    qpu_file = files_list[0]
                    content = qpu_file.get("content", "{}")
                    if isinstance(content, str):
                        qpu_data = json.loads(content)
                    else:
                        qpu_data = content
                else:
                    logger.error("No QPU data file found in evidence")
                    return evidence_data
            else:
                # Legacy: evidence_data is the QPU data directly
                qpu_data = evidence_data

            # Generate IDs and timestamp
            evidence_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc).isoformat()

            # Extract QPU metrics from data (qpu_data may be a dict or a JSON array)
            data_dict = qpu_data if isinstance(qpu_data, dict) else {}
            qpu_id = data_dict.get("qpu_id", str(uuid.uuid4()))

            # Build Clouditor evidence structure
            transformed = {
                "timestamp": current_time,
                "id": evidence_id,
                "targetOfEvaluationId": toe_id or "00000000-0000-0000-0000-000000000000",
                "toolId": "QPU Collector",
                "resource": {
                    "qpu": {
                        "id": qpu_id,
                        "name": data_dict.get("name", "FOKUS-QPU"),
                        "oneQubitGateErrorRate": str(data_dict.get("OneQubitGateErrorRate", "9.999999999998899e-05")),
                        "twoQubitGateErrorRate": str(data_dict.get("TwoQubitGateErrorRate", "0.00019998999999992773")),
                        "spamErrorRate": str(data_dict.get("SPAMErrorRate", "9.999999999998899e-05")),
                        "errorCorrectionEnabled": data_dict.get("ErrorCorrectionEnabled", False),
                        "creationTime": current_time,
                        "raw": json.dumps(qpu_data)  # Include full raw data
                    }
                }
            }

            logger.info(f"QPU data transformed for Clouditor, evidence_id: {evidence_id}")
            return transformed

        except Exception as e:
            logger.error(f"Error transforming QPU data: {e}")
            import traceback
            traceback.print_exc()
            return evidence_data

    def prepare_evidence_flexible(self, thing: dict, evidence_config: dict):
        """
        Flexible evidence preparation based on dynamic configuration.

        Args:
            thing: The Thing object from Ditto
            evidence_config: Evidence configuration dict
                {
                    "type": "thing|zip|files|specific|auto",
                    "files": ["file1.txt", "file2.json"],  # For files/specific type
                    "include": ["*.py", "*.h5"],            # For zip type
                    "exclude": [".git/*", "*.pyc"]          # For zip type
                    "include_features": ["components"]      # For thing type
                }

        Returns:
            Prepared evidence data
        """
        logger.info(f"Preparing flexible evidence: type={evidence_config.get('type')}")

        evidence_type = evidence_config.get("type", "thing")

        if evidence_type == "thing":
            # Return full thing or filtered thing
            include_features = evidence_config.get("include_features")
            if include_features:
                return {
                    "thingId": thing.get("thingId"),
                    "attributes": thing.get("attributes", {}),
                    "features": {k: v for k, v in thing.get("features", {}).items() if k in include_features}
                }
            return thing

        elif evidence_type == "zip":
            # Create ZIP with pattern filtering
            return self._create_zip_flexible(thing, evidence_config)

        elif evidence_type in ["files", "specific"]:
            # Get specific files
            return self._get_files_flexible(thing, evidence_config)

        else:
            logger.warning(f"Unknown evidence type: {evidence_type}, returning full thing")
            return thing

    def _create_zip_flexible(self, thing: dict, evidence_config: dict):
        """
        Create ZIP archive with flexible pattern filtering.
        """
        import fnmatch
        import zipfile
        import tempfile

        # Check if this is a FILE type with an existing file
        category = thing.get("attributes", {}).get("category")
        file_path = thing.get("attributes", {}).get("file_path")
        filename = thing.get("attributes", {}).get("filename", "")

        # If it's a FILE type with an existing file, return it directly
        if category == "FILE" and file_path and os.path.exists(file_path):
            logger.info(f"FILE type detected with existing file: {file_path}")
            # Check if it's already a zip file
            if filename.endswith('.zip') or file_path.endswith('.zip'):
                logger.info(f"Returning existing ZIP file: {file_path}")
                return {"zip_path": file_path, "files_count": 1}
            else:
                # For non-zip files, create a zip containing the single file
                temp_dir = tempfile.mkdtemp()
                thing_id = thing.get("thingId", "unknown").replace(":", "_")
                zip_path = os.path.join(temp_dir, f"{thing_id}.zip")

                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, filename)

                logger.info(f"Created ZIP with single file at: {zip_path}")
                return {"zip_path": zip_path, "files_count": 1}

        # Get repository path from thing attributes (for GitHub/repo-based things)
        repo_path = thing.get("attributes", {}).get("github")
        if not repo_path or not os.path.exists(repo_path):
            logger.error(f"Repository path not found or doesn't exist: {repo_path}")
            return None

        include_patterns = evidence_config.get("include", ["*"])
        exclude_patterns = evidence_config.get("exclude", [])

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        thing_id = thing.get("thingId", "unknown").replace(":", "_")
        zip_path = os.path.join(temp_dir, f"{thing_id}.zip")

        # Create ZIP with filtered files
        files_added = 0
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Check if matches include patterns
                    matches_include = any(fnmatch.fnmatch(file, pattern) for pattern in include_patterns)
                    if not matches_include:
                        continue

                    # Check if matches exclude patterns
                    matches_exclude = any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns)
                    if matches_exclude:
                        continue

                    try:
                        zipf.write(file_path, rel_path)
                        files_added += 1
                    except Exception as e:
                        logger.error(f"Error adding file to ZIP: {file_path}, error: {e}")

        logger.info(f"Created ZIP with {files_added} files at: {zip_path}")
        return {"zip_path": zip_path, "files_count": files_added}

    def _get_files_flexible(self, thing: dict, evidence_config: dict):
        """
        Get specific files from thing based on flexible configuration.
        """
        files_list = evidence_config.get("files", [])

        # Try to find files in Repository_file_tree feature
        file_tree = thing.get("features", {}).get("Repository_file_tree", {}).get("properties", {})

        result_files = []
        for file_name in files_list:
            # Search for file in file tree
            for file_key, file_info in file_tree.items():
                if isinstance(file_info, dict) and file_info.get("name") == file_name:
                    file_path = file_info.get("path")
                    if file_path and os.path.exists(file_path):
                        # Read file content for transformation
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                        except Exception as e:
                            logger.error(f"Error reading file {file_path}: {e}")
                            content = None

                        result_files.append({
                            "name": file_name,
                            "path": file_path,
                            "hash": file_info.get("hash"),
                            "size": os.path.getsize(file_path),
                            "content": content
                        })
                        break

        logger.info(f"Found {len(result_files)} files out of {len(files_list)} requested")
        return {"files": result_files}

    def apply_transform_flexible(self, thing: dict, evidence_data: dict, transform_config: str = None):
        """
        Apply transformation to evidence data based on flexible configuration.

        Args:
            thing: The Thing object
            evidence_data: Prepared evidence data
            transform_config: Transform configuration (string name or JSON)

        Returns:
            Transformed evidence data
        """
        if not transform_config:
            return evidence_data

        try:
            # Try to parse as JSON for custom mapping
            transform_dict = json.loads(transform_config)
            return self._apply_mapping(thing, transform_dict)
        except (json.JSONDecodeError, TypeError):
            # It's a named transformer - map common names to actual transform methods
            transform_mapping = {
                "qpu_clouditor": "_transform_qpu_data",
                "qpu_data": "_transform_qpu_data"
            }

            # Get the actual method name
            method_name = transform_mapping.get(transform_config, f"_transform_{transform_config}")
            transformer_func = getattr(self, method_name, None)

            if transformer_func:
                toe_id = thing.get("attributes", {}).get("toe_id")
                return transformer_func(evidence_data, toe_id)
            else:
                logger.warning(f"Transform function not found: {method_name}")
                return evidence_data
