import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.controller import Controller

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class TestController(unittest.TestCase):
    def setUp(self):
        self.controller = Controller()
        self.test_toeid = "123456789"
        self.test_level = "test.bom"
        self.test_payload = {
            "thingId": "",
            "policyId": "",
            "attributes": {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6",
                "serialNumber": "urn:uuid:23a3c6b3-038e-443e-b080-ddfd0a22f211",
                "BomType": "cbom.certificate",
                "certificateType": "root",
                "certificateUsage": "server-authentication",
                "hashAlgorithm": "SHA-256"
            },
            "features": {
                "metadata": {
                    "properties": {
                        "timestamp": "2025-02-19T15:11:07Z",
                        "component": {
                            "type": "application",
                            "name": "my application",
                            "version": "1.0",
                            "publisher": "Example Corp",
                            "description": "Test application for certificate CBOM",
                            "license": {
                                "id": "MIT"
                            }
                        },
                        "tools": [
                            {
                                "name": "CBOM Generator",
                                "version": "2.1.0"
                            }
                        ]
                    }
                },
                "components": {
                    "properties": {
                        "components": [
                            {
                                "name": "Sectigo Public Server Authentication Root E46",
                                "type": "cryptographic-asset",
                                "bom-ref": "crypto/certificate/Sectigo Public Server Authentication Root E46@384 bit",
                                "version": "1.0",
                                "purl": "pkg:cert/sectigo/public-server-auth-root-e46@1.0",
                                "properties": [
                                    {
                                        "name": "validity-not-before",
                                        "value": "2023-01-01T00:00:00Z"
                                    },
                                    {
                                        "name": "validity-not-after",
                                        "value": "2043-01-01T23:59:59Z"
                                    },
                                    {
                                        "name": "serial-number",
                                        "value": "0a:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99"
                                    },
                                    {
                                        "name": "signature-algorithm",
                                        "value": "ECDSA-SHA384"
                                    },
                                    {
                                        "name": "key-size",
                                        "value": "384"
                                    },
                                    {
                                        "name": "thumbprint-sha256",
                                        "value": "ab01cd23ef45gh67ij89kl01mn23op45qr67st89uv01wx23yz45ab67cd89"
                                    }
                                ],
                                "issuer": {
                                    "organization": "Sectigo Limited",
                                    "commonName": "Sectigo Public Server Authentication Root E46",
                                    "country": "GB"
                                },
                                "subject": {
                                    "organization": "Sectigo Limited",
                                    "commonName": "Sectigo Public Server Authentication Root E46",
                                    "country": "GB"
                                }
                            }
                        ]
                    }
                },
                "vulnerabilities": {
                    "properties": {
                        "vulnerabilities": [
                            {
                                "id": "EXAMPLE-2023-001",
                                "affects": [
                                    {
                                        "ref": "crypto/certificate/Sectigo Public Server Authentication Root E46@384 bit"
                                    }
                                ],
                                "ratings": [
                                    {
                                        "method": "CVSSv3",
                                        "score": 3.4,
                                        "severity": "LOW"
                                    }
                                ],
                                "description": "Example low severity vulnerability for testing"
                            }
                        ]
                    }
                }
            },
            "_metadata": {
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
                    },
                    "authors": [
                        {
                            "name": "John Doe",
                            "email": "john.doe@example.com"
                        }
                    ],
                    "lifecycles": [
                        {
                            "phase": "testing"
                        }
                    ]
                }
            }
        }
        
    @patch('requests.Session')
    @patch.object(Controller, '_Controller__create_policy')
    def test_create(self, mock_create_policy, mock_session):
        """Test the create functionality of the Controller"""
        
        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Setup create response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = json.dumps({"status": "created"})
        mock_response.json.return_value = {"status": "created"}
        
        # Setup policy creation
        mock_create_policy.return_value = (MagicMock(), "cobalt:policy")
        
        # Configure PUT response
        mock_session_instance.put.return_value = mock_response
        
        # Call create method
        result = self.controller.create_in_ditto(
            json.dumps(self.test_payload), 
            self.test_toeid, 
            self.test_level
        )
        
        print(f"Result: {result}")
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 201)
        
        # Log and return result for saving
        logger.info(f"CREATE Test Result: {result}")
        return result
        
    @patch('requests.Session')
    def test_read(self, mock_session):
        """Test the read functionality of the Controller"""
        
        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Setup read response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "thingId": f"{self.test_level}:{self.test_toeid}",
            "policyId": "cobalt:policy",
            "attributes": {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6"
            }
        }
        
        # Configure GET response
        mock_session_instance.get.return_value = mock_response
        
        # Call read method
        result = self.controller.read_item(self.test_toeid, self.test_level)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["attributes"]["bomFormat"], "CycloneDX")
        
        # Log and return result for saving
        logger.info(f"READ Test Result: {result}")
        return result
        
    @patch('requests.Session')
    @patch.object(Controller, 'read_item')
    def test_update(self, mock_read_item, mock_session):
        """Test the update functionality of the Controller"""
        
        # Mock the existing item
        mock_read_item.return_value = {
            "thingId": f"{self.test_level}:{self.test_toeid}",
            "policyId": "cobalt:policy",
            "attributes": {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6"
            }
        }
        
        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Setup update response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"status": "updated"})
        mock_response.json.return_value = {"status": "updated"}
        
        # Configure PUT response
        mock_session_instance.put.return_value = mock_response
        
        # Update the payload
        updated_payload = self.test_payload.copy()
        updated_payload["attributes"]["specVersion"] = "1.7"
        
        # Call update method
        result = self.controller.update_item(
            self.test_toeid, 
            self.test_level, 
            updated_payload
        )
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        
        # Log and return result for saving
        logger.info(f"UPDATE Test Result: {result}")
        return result
        
    @patch('requests.Session')
    @patch.object(Controller, 'read_item')
    def test_delete(self, mock_read_item, mock_session):
        """Test the delete functionality of the Controller"""
        
        # Setup the read_item mock to first return an item (before deletion)
        # and then None after deletion (verification)
        mock_read_item.side_effect = [
            # First call - Check if item exists before deletion
            {
                "thingId": f"{self.test_level}:{self.test_toeid}",
                "policyId": "cobalt:policy"
            },
            # Second call - Verification after deletion
            None
        ]
        
        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Setup delete response - Status code 204 No Content is typical for successful DELETE
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        
        # Configure DELETE response
        mock_session_instance.delete.return_value = mock_response
        
        # Call delete method
        result = self.controller.delete_item(self.test_toeid, self.test_level)
        
        # Verify mock_read_item was called exactly twice
        self.assertEqual(mock_read_item.call_count, 2)
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 204)
        self.assertEqual(result["message"], "Thing deleted successfully")
        
        # Log and return result for saving
        logger.info(f"DELETE Test Result: {result}")
        return result


def save_test_result(test_name, result):
    """Save test result to a file"""
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    filename = os.path.join(results_dir, f"{test_name}_result.json")
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Test result saved to {filename}")


# Replace the if __name__ == '__main__': section with this code:

if __name__ == '__main__':
    # Interactive test runner
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Create test instance
    test_instance = TestController('test_create')
    
    # Track which tests have been run
    tests_run = {
        '1': False,  # Create
        '2': False,  # Read
        '3': False,  # Update
        '4': False,  # Delete
    }
    
    # Map of test options to test methods
    test_map = {
        '1': ('test_create', 'Create'),
        '2': ('test_read', 'Read'),
        '3': ('test_update', 'Update'),
        '4': ('test_delete', 'Delete'),
    }
    
    # Ensure we're not in a non-interactive environment
    import sys
    if not sys.stdin.isatty():
        print("Warning: Running in a non-interactive environment. Will prompt for choices anyway.")
    
    while not all(tests_run.values()):
        # Show menu with clear separation
        print("\n" + "="*50)
        print("=== Controller Test Menu ===")
        print("="*50)
        print("Select a test to run:")
        for key, (_, name) in test_map.items():
            status = "✓" if tests_run[key] else " "
            print(f"{key}. [{status}] Test {name}")
        print("q. Quit")
        print("="*50)
        
        # Force flush stdout to ensure the prompt is visible
        sys.stdout.flush()
        
        # Get user choice with a timeout to ensure it doesn't hang
        import time
        print("\nWaiting for your input... (1-4 or q)")
        choice = None
        
        # Try to get input with a special handling to prevent hanging
        try:
            # Use a more explicit prompt
            choice = input(">>> ").lower()
            print(f"You selected: {choice}")
        except Exception as e:
            print(f"Error getting input: {e}")
            # Provide a fallback option
            print("Using default choice: 1")
            choice = '1'
        
        if choice == 'q':
            print("Exiting test runner.")
            break
        
        if choice not in test_map:
            print("Invalid choice. Please select a valid option.")
            continue
        
        # Run the selected test
        test_method, test_name = test_map[choice]
        print(f"\nRunning {test_name} test...")
        
        # Set the test method
        test_instance._testMethodName = test_method
        
        # Run the test
        result = test_runner.run(test_instance)
        
        # Mark test as run
        tests_run[choice] = True
        
        # If test passed, save the result
        if result.wasSuccessful():
            # Get the test method
            method = getattr(test_instance, test_method)
            
            # Save test result using a mock context for the patched dependencies
            with patch('requests.Session'):
                if test_method == 'test_create':
                    with patch.object(Controller, '_Controller__create_policy'):
                        test_result = method()
                        save_test_result(test_name.lower(), test_result)
                elif test_method == 'test_update' or test_method == 'test_delete':
                    with patch.object(Controller, 'read_item'):
                        test_result = method()
                        save_test_result(test_name.lower(), test_result)
                else:
                    test_result = method()
                    save_test_result(test_name.lower(), test_result)
        
        # Check if all tests have been run
        if all(tests_run.values()):
            print("\nAll tests have been run!")
            break
        
        # Add a pause between tests
        print("\nPress Enter to continue to the next test selection...")
        try:
            input()
        except:
            time.sleep(2)  # Alternative delay if input fails