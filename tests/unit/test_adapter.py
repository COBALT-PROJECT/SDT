import unittest
import os
import json
import sys
import logging
import time
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.adapter import DTModelAdapter
from core.controller import Controller

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class TestDTModelAdapter(unittest.TestCase):
    """Unit tests for DTModelAdapter class"""
    
    def setUp(self):
        self.adapter = DTModelAdapter()
        self.cyclone_example = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": "urn:uuid:23a3c6b3-038e-443e-b080-ddfd0a22f211",
            "version": 1,
            "metadata": {
                "timestamp": "2025-02-19T15:11:07Z",
                "component": {
                    "type": "application",
                    "name": "my application",
                    "version": "1.0"
                }
            },
            "components": [
                {
                    "name": "Sectigo Public Server Authentication Root E46",
                    "type": "cryptographic-asset",
                    "bom-ref": "crypto/certificate/Sectigo Public Server Authentication Root E46@384 bit",
                    "cryptoProperties": {
                        "assetType": "certificate",
                        "certificateProperties": {
                            "subjectName": "Sectigo Public Server Authentication Root E46",
                            "issuerName": "C = GB, O = Sectigo Limited, CN = Sectigo Public Server Authentication Root E46",
                            "notValidBefore": "2021-03-22T00:00:00Z",
                            "notValidAfter": "2046-03-21T23:59:59Z",
                            "signatureAlgorithmRef": "crypto/algorithm/ecdsa-with-SHA384@unknown",
                            "subjectPublicKeyRef": "crypto/key/384 bit@id-ecPublicKey",
                            "certificateFormat": "X.509",
                            "certificateExtension": "crt"
                        }
                    }
                }
            ]
        }
    
    def test_detect_bom_type(self):
        """Test the detect_bom_type method for different BOM types"""
        
        # Test CBOM detection with certificate component
        result = self.adapter.detect_bom_type(self.cyclone_example)
        self.assertEqual(result, "cbom.certificate")
        
        # Test SBOM detection
        sbom_example = self.cyclone_example.copy()
        sbom_example["components"][0]["type"] = "library"
        result = self.adapter.detect_bom_type(sbom_example)
        self.assertEqual(result, "sbom")
        
        # Test HBOM detection
        hbom_example = self.cyclone_example.copy()
        hbom_example["components"][0]["type"] = "device"
        result = self.adapter.detect_bom_type(hbom_example)
        self.assertEqual(result, "hbom")
        
        # Test VEX detection
        vex_example = {"vulnerabilities": [{"id": "CVE-2023-1234"}]}
        result = self.adapter.detect_bom_type(vex_example)
        self.assertEqual(result, "vex")
        
        # Test SaasBOM detection
        saasbom_example = {"dependencies": [], "services": []}
        result = self.adapter.detect_bom_type(saasbom_example)
        self.assertEqual(result, "saasbom")
        
        # Test default detection
        generic_example = {"somefield": "somevalue"}
        result = self.adapter.detect_bom_type(generic_example)
        self.assertEqual(result, "boms")

    def test_convert_urn(self):
        """Test the convert_urn method for different URN formats"""
        
        # Test standard URN format
        result = self.adapter.convert_urn("urn:uuid:23a3c6b3-038e-443e-b080-ddfd0a22f211")
        self.assertEqual(result, "urn.uuid:23a3c6b3-038e-443e-b080-ddfd0a22f211")
        
        # Test another format
        result = self.adapter.convert_urn("test:value:content")
        self.assertEqual(result, "test.value:content")
        
        # Test with insufficient parts
        result = self.adapter.convert_urn("test:value")
        self.assertEqual(result, "test:value")
        
        # Test with no colons
        result = self.adapter.convert_urn("testvalue")
        self.assertEqual(result, "testvalue")

    @patch('logging.getLogger')
    def test_validate_cyclone(self, mock_logger):
        """Test the validate_cyclone method"""
        
        # Test with valid payload
        result = self.adapter.validate_cyclone(self.cyclone_example)
        self.assertTrue(result)
        
        # Test with invalid payload
        invalid_example = {"someField": "someValue"}
        result = self.adapter.validate_cyclone(invalid_example)
        self.assertFalse(result)

    @patch('core.controller.Controller.create_in_ditto')
    def test_from_cyclone(self, mock_create_in_ditto):
        """Test the from_cyclone method with the example payload"""
        
        # Setup mock
        mock_create_in_ditto.return_value = {"success": True, "status_code": 201}
        
        # Convert the example to JSON string
        cyclone_json = json.dumps(self.cyclone_example)
        
        # Call the method
        transformed, serial_number, bom_type = self.adapter.from_cyclone(cyclone_json, "test_name")
        
        # Assertions
        self.assertIsNotNone(transformed)
        self.assertEqual(transformed["attributes"]["bomFormat"], "CycloneDX")
        self.assertEqual(transformed["attributes"]["specVersion"], "1.6")
        self.assertEqual(transformed["attributes"]["serialNumber"], "urn:uuid:23a3c6b3-038e-443e-b080-ddfd0a22f211")
        self.assertEqual(transformed["attributes"]["BomType"], "cbom.certificate")
        
        # Check if features contains the components
        self.assertIn("components", transformed["features"])
        
        # Check if the serial number was properly converted
        self.assertEqual(serial_number, "urn.uuid:23a3c6b3-038e-443e-b080-ddfd0a22f211")
        
        # Check if the BOM type was properly detected
        self.assertEqual(bom_type, "cbom.certificate")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b'test content')
    def test_get_file_hash(self, mock_open):
        """Test the get_file_hash method"""
        
        # Call the method
        result = self.adapter.get_file_hash("test_file.txt")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 64)  # SHA-256 hash is 64 chars in hex
        mock_open.assert_called_once_with("test_file.txt", "rb")

    @patch('requests.post')
    def test_send_to_controller(self, mock_post):
        """Test the send_to_controller method"""
        
        # Setup mock
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        # Call the method
        payload = {"test": "payload"}
        result = self.adapter.send_to_controller(payload)
        
        # Assertions
        self.assertEqual(result, mock_response)
        mock_post.assert_called_once()
        # Check if the URL and headers are correct
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers'], {'Content-Type': 'application/json'})
        self.assertEqual(args[0], 'http://127.0.0.1:8000/api/SDT/push/')

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('git.Repo.clone_from')
    @patch('core.controller.Controller.create_in_ditto')
    def test_fetch_push_save_repo(self, mock_create_in_ditto, mock_clone_from, 
                                  mock_rmtree, mock_exists, mock_makedirs):
        """Test the fetch_push_save_repo method"""
        
        # Setup mocks
        mock_exists.return_value = True
        mock_create_in_ditto.return_value = {"success": True, "status_code": 201}
        mock_repo = MagicMock()
        mock_clone_from.return_value = mock_repo
        
        # Call the method
        result = self.adapter.fetch_push_save_repo("https://github.com/example/repo.git")
        
        # Assertions
        self.assertEqual(result, "DT created")
        mock_makedirs.assert_called_once()
        mock_exists.assert_called_once()
        mock_rmtree.assert_called_once()
        mock_clone_from.assert_called_once()

    @patch('requests.get')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('core.adapter.DTModelAdapter.get_file_hash')
    def test_fetch_push_save_file(self, mock_get_file_hash, mock_open, mock_makedirs, mock_get):
        """Test the fetch_push_save_file method"""
        
        # Setup mocks
        mock_response = MagicMock()
        mock_response.content = b'file content'
        mock_get.return_value = mock_response
        mock_get_file_hash.return_value = "test_hash_value"
        
        # Call the method
        result = self.adapter.fetch_push_save_file("https://github.com/example/repo/blob/main/file.h5")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["thingId"], "toe.ai.h5")
        self.assertEqual(result["attributes"]["file_name"], "file.h5")
        self.assertEqual(result["attributes"]["github"], "https://github.com/example/repo/blob/main/file.h5")
        self.assertEqual(result["features"]["file"]["properties"]["hash"], "test_hash_value")
        mock_makedirs.assert_called_once()
        mock_get.assert_called_once()
        mock_open.assert_called_once()

    @patch('requests.Session')
    def test_from_clouditor(self, mock_session):
        """Test the from_clouditor method"""
        
        # Setup mock data
        clouditor_data = {
            "id": "test_id",
            "resource": {
                "@type": "compute",
                "id": "resource_id",
                "name": "test_resource",
                "creationTime": "2025-02-19T15:11:07Z",
                "labels": {"key": "value"},
                "internetAccessibleEndpoint": False,
                "raw": {},
                "custom_property": "custom_value"
            }
        }
        
        # Call method
        result = self.adapter.from_clouditor(clouditor_data)
        
        # Basic assertions on structure
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        if result:  # If we got a valid result
            self.assertEqual(result[0]["policyId"], "cobalt:policy")
            self.assertEqual(result[0]["definition"], "cobalt:clouditor-resource:0.0.1")
            self.assertIn("custom_property", result[0]["features"])


if __name__ == '__main__':
    print("Running tests for DTModelAdapter...")
    
    # Create an interactive menu for testing
    while True:
        print("\n" + "="*50)
        print("=== DTModelAdapter Test Menu ===")
        print("="*50)
        print("1. Test detect_bom_type")
        print("2. Test convert_urn")
        print("3. Test from_cyclone")
        print("4. Test fetch_push_save_repo")
        print("5. Test fetch_push_save_file")
        print("6. Test validate_cyclone")
        print("7. Test get_file_hash")
        print("8. Test send_to_controller")
        print("9. Test from_clouditor")
        print("10. Run All Tests")
        print("q. Quit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-10 or q): ").lower()
        
        if choice == 'q':
            print("Exiting test runner.")
            break
        
        test_suite = unittest.TestSuite()
        runner = unittest.TextTestRunner(verbosity=2)
        
        if choice == '1':
            test_suite.addTest(TestDTModelAdapter('test_detect_bom_type'))
        elif choice == '2':
            test_suite.addTest(TestDTModelAdapter('test_convert_urn'))
        elif choice == '3':
            test_suite.addTest(TestDTModelAdapter('test_from_cyclone'))
        elif choice == '4':
            test_suite.addTest(TestDTModelAdapter('test_fetch_push_save_repo'))
        elif choice == '5':
            test_suite.addTest(TestDTModelAdapter('test_fetch_push_save_file'))
        elif choice == '6':
            test_suite.addTest(TestDTModelAdapter('test_validate_cyclone'))
        elif choice == '7':
            test_suite.addTest(TestDTModelAdapter('test_get_file_hash'))
        elif choice == '8':
            test_suite.addTest(TestDTModelAdapter('test_send_to_controller'))
        elif choice == '9':
            test_suite.addTest(TestDTModelAdapter('test_from_clouditor'))
        elif choice == '10':
            test_suite.addTest(TestDTModelAdapter('test_detect_bom_type'))
            test_suite.addTest(TestDTModelAdapter('test_convert_urn'))
            test_suite.addTest(TestDTModelAdapter('test_from_cyclone'))
            test_suite.addTest(TestDTModelAdapter('test_fetch_push_save_repo'))
            test_suite.addTest(TestDTModelAdapter('test_fetch_push_save_file'))
            test_suite.addTest(TestDTModelAdapter('test_validate_cyclone'))
            test_suite.addTest(TestDTModelAdapter('test_get_file_hash'))
            test_suite.addTest(TestDTModelAdapter('test_send_to_controller'))
            test_suite.addTest(TestDTModelAdapter('test_from_clouditor'))
        else:
            print("Invalid choice. Please select a valid option.")
            continue
        
        runner.run(test_suite)