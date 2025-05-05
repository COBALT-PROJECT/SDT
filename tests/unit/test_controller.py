import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.controller import Controller

class TestController(unittest.TestCase):
    def setUp(self):
        self.controller = Controller()
        self.test_toeid = "b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e"
        self.test_level = "toe.ai.h5"
        
    @patch('requests.get')
    def test_read_item(self, mock_get):
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"path": "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/evidence/testevidence"}
        mock_get.return_value = mock_response
        
        result = self.controller.read_item(self.test_toeid, self.test_level)
        self.assertEqual(result, "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/evidence/testevidence")
        
    @patch('requests.post')
    def test_create_in_ditto(self, mock_post):
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        payload = json.dumps({"name": "test", "payload": {"key": "value"}})
        result = self.controller.create_in_ditto(payload)
        self.assertTrue(result)
        
    @patch('requests.put')
    def test_update_item(self, mock_put):
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        payload = {"key": "value"}
        result = self.controller.update_item(self.test_toeid, self.test_level, payload)
        self.assertTrue(result)
        
    @patch('requests.delete')
    def test_delete_item(self, mock_delete):
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        result = self.controller.delete_item(self.test_toeid, self.test_level)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()