import pytest
import os
import json
from unittest.mock import MagicMock
from core.util import FileUtils
from core.evidence_provider import EvidenceProvider
from core.translator import Translator
from core.adapter_all import DTModelAdapter

# --- Global Fixtures ---

@pytest.fixture
def mock_thing():
    """Returns a sample Eclipse Ditto 'thing' object."""
    return {
        "thingId": "cobalt:test-device",
        "policyId": "cobalt:policy",
        "attributes": {
            "category": "AI usecase",
            "sourceType": "CycloneDX",
            "github": "https://github.com/COBALT-PROJECT/SDT"
        },
        "features": {
            "Repository_file_tree": {
                "properties": {
                    "file1": {"name": "sbom.json"},
                    "file2": {"name": "script.py"}
                }
            }
        }
    }

@pytest.fixture
def sample_mapping_config():
    """Returns a sample evidence format mapping for EvidenceProvider."""
    return {
        "category": ["AI usecase"],
        "sourceType": ["CycloneDX"],
        "file_extensions": [".json"],
        "exclude_deleted": True
    }

# --- Utility Tests (core/util.py) ---

def test_file_utils_zip_naming(tmp_path):
    """Tests that FileUtils generates a zip filename with the correct prefix and toe_id."""
    evidence_dir = tmp_path / "test_evidence"
    evidence_dir.mkdir()
    (evidence_dir / "file.txt").write_text("content")
    
    toe_id = "test-toe"
    zip_path, zip_filename = FileUtils.zip_file(str(evidence_dir), toe_id)
    
    assert zip_filename.startswith(f"evidence_{evidence_dir.name}_{toe_id}_")
    assert zip_filename.endswith(".zip")
    assert os.path.exists(zip_path)
    
    # Clean up
    if os.path.exists(zip_path):
        os.remove(zip_path)

def test_file_utils_file_response(tmp_path):
    """Tests that FileUtils correctly generates a FileResponse."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    
    response = FileUtils.file_response(str(test_file))
    assert response.path == str(test_file)
    assert response.filename == "test.txt"
    # FastAPI/Starlette will auto-detect media_type for .txt files as 'text/plain'
    assert "text/plain" in response.media_type 

# --- Evidence Provider Tests (core/evidence_provider.py) ---

def test_thing_matches_filters_success(mock_thing, sample_mapping_config):
    """Verifies that a thing matching all criteria returns True."""
    ep = EvidenceProvider()
    # Mocking filters expected by the internal method
    result = ep._thing_matches_filters(mock_thing, sample_mapping_config)
    assert result is True

def test_thing_matches_filters_mismatch_category(mock_thing, sample_mapping_config):
    """Verifies that a thing with a different category returns False."""
    ep = EvidenceProvider()
    mock_thing["attributes"]["category"] = "Quantum usecase"
    result = ep._thing_matches_filters(mock_thing, sample_mapping_config)
    assert result is False

def test_topic_matches_wildcard():
    """Tests MQTT topic wildcard matching."""
    ep = EvidenceProvider()
    assert ep._topic_matches("cobalt/thing/1/created", ["cobalt/thing/*/created"]) is True
    assert ep._topic_matches("cobalt/thing/1/updated", ["cobalt/thing/*/created"]) is False

# --- Translator Tests (core/translator.py) ---

def test_translator_initialization():
    """Ensures Translator initializes without error."""
    trs = Translator()
    assert trs is not None

# --- Adapter & Data Mapping Tests (core/adapter_all.py) ---

def test_adapter_from_cyclone_mapping():
    """Verifies that DTModelAdapter correctly transforms a CycloneDX BOM to Ditto format."""
    adapter = DTModelAdapter()
    
    # Using a subset of juice-shop v11.1.2 bom.json for testing
    sample_bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.2",
        "serialNumber": "urn:uuid:1f860713-54b9-4253-ba5a-9554851904af",
        "version": 1,
        "metadata": {
            "timestamp": "2020-08-03T03:20:53.771Z",
            "component": {
                "name": "juice-shop",
                "version": "11.1.2"
            }
        },
        "components": [
            {
                "name": "body-parser",
                "version": "1.19.0",
                "purl": "pkg:npm/body-parser@1.19.0"
            }
        ]
    }
    
    # The adapter expects a JSON string
    json_input = json.dumps(sample_bom)
    result = adapter.from_cyclone(json_input)
    
    # Check if result is already a dict or still a JSON string
    if isinstance(result, str):
        result = json.loads(result)
    
    # Verify expected DITTO structure
    # Based on adapter_all.py: attributes include top-level fields
    assert "attributes" in result
    assert result["attributes"]["bomFormat"] == "CycloneDX"
    assert result["attributes"]["specVersion"] == "1.2"
    
    # Verify features (usually components are mapped to features)
    assert "features" in result
    # The exact mapping depends on adapter_all.py implementation details
    # but we expect at least the metadata component or the components list to be present
    assert len(result["features"]) > 0

def test_adapter_invalid_json():
    """Verifies that DTModelAdapter handles invalid JSON gracefully."""
    adapter = DTModelAdapter()
    with pytest.raises(json.JSONDecodeError):
        adapter.from_cyclone("{ invalid json }")
