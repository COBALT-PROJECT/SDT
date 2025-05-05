import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from core.evidence_provider import EvidenceProvider
from core.controller import Controller

class TestEvidenceProvider(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.evidence_provider = EvidenceProvider(self.controller)
        self.test_toeid = "b10359fb-7d9e-4bf2-b83b-8b0244a0dd4e"
        self.test_level = "toe.ai.h5"
        
    def test_get_evidence_invalid_level(self):
        result = self.evidence_provider.get_evidence(self.test_toeid, "invalid_level")
        self.assertEqual(result["message"], "Invalid evidence level")
        
    @patch('os.path.exists')
    def test_get_evidence_nonexistent_dir(self, mock_exists):
        # Mock the controller response
        self.controller.read_item.return_value = "/nonexistent/path"
        mock_exists.return_value = False
        
        result = self.evidence_provider.get_evidence(self.test_toeid, self.test_level)
        self.assertEqual(result["error"], "No evidence directory found")
        
    @patch('os.path.exists')
    @patch('shutil.make_archive')
    @patch('tempfile.gettempdir')
    def test_get_evidence_success(self, mock_tempdir, mock_archive, mock_exists):
        # Mock the controller response
        self.controller.read_item.return_value = "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/evidence/testevidence"
        mock_exists.return_value = True
        mock_tempdir.return_value = "/tmp"
        mock_archive.return_value = "/tmp/evidence_testevidence_123456.zip"
        
        # We can't easily test FileResponse, so we'll patch it
        with patch('fastapi.responses.FileResponse') as mock_file_response:
            mock_file_response.return_value = {"status": "success"}
            result = self.evidence_provider.get_evidence(self.test_toeid, self.test_level)
            # Check that the FileResponse was called
            mock_file_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()