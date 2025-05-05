import pytest
import os
import sys
import json
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Add the project root to the path so we can import modules properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your app and modules
from core.controller import Controller
from core.evidence_provider import EvidenceProvider
from core.adapter import DTModelAdapter
from sdt_service import app

# Test data fixture
@pytest.fixture
def test_data():
    return {
        "toeid": "b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e",
        "level": "toe.ai.h5",
        "sample_payload": {
            "name": "test_device",
            "metadata": {
                "id": "b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e"
            },
            "properties": {
                "status": "active"
            }
        }
    }

# Mock controller fixture
@pytest.fixture
def mock_controller():
    controller = MagicMock()
    controller.read_item.return_value = "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/evidence/testevidence"
    controller.create_in_ditto.return_value = True
    controller.update_item.return_value = True
    controller.delete_item.return_value = True
    return controller

# Evidence provider with mock controller
@pytest.fixture
def evidence_provider(mock_controller):
    return EvidenceProvider(mock_controller)

# FastAPI test client
@pytest.fixture
def client():
    return TestClient(app)

# Test environment setup/teardown
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Setup code executed before all tests
    original_env = dict(os.environ)
    os.environ["TESTING"] = "True"
    
    # Create any necessary test directories or files
    test_evidence_dir = "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/evidence/testevidence"
    os.makedirs(test_evidence_dir, exist_ok=True)
    
    # Return control to tests
    yield
    
    # Teardown code executed after all tests
    os.environ.clear()
    os.environ.update(original_env)