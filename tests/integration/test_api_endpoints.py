import unittest
from fastapi.testclient import TestClient
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sdt_service import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_toeid = "b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e"
        self.test_level = "toe.ai.h5"
        
    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "SDT Service Interface"})
        
    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
        
    def test_read_item(self):
        response = self.client.get(f"/api/SDT/read/?toeid={self.test_toeid}&level={self.test_level}")
        self.assertEqual(response.status_code, 200)
        
    def test_evidence_endpoint(self):
        response = self.client.get(f"/api/SDT/evidence/watchtower/?toeid={self.test_toeid}&level={self.test_level}")
        # Check for either success (200) or file not found (404)
        self.assertIn(response.status_code, [200, 404])

if __name__ == '__main__':
    unittest.main()