import unittest
import os
import json
import sys
import logging
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.controller import Controller

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class TestControllerIntegration(unittest.TestCase):
    """Integration tests for Controller with real Ditto server"""
    
    def setUp(self):
        self.controller = Controller()
        self.test_toeid = "123456789"
        self.test1_level = "boms"
        self.test2_level = "test2.bom"
        self.test3_level = "test3.bom"
        self.test4_level = "test4.bom"
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
        
    
    def test_1_create(self):
        """Test creating a thing in Ditto"""
        
        # Call create method with real data
        result = self.controller.create_in_ditto(
            json.dumps(self.test_payload), 
            self.test_toeid, 
            self.test1_level
        )
        
        # Print and log the result
        print(f"CREATE Result: {result}")
        logger.info(f"CREATE Integration Test Result: {result}")
        
        # Assertions
        self.assertIn("success", result, "The 'success' key is missing in the result.")
        self.assertTrue(result["success"])
        # Print status code if assertion would fail
        if result["status_code"] not in [200, 201, 202, 204]:
            print(f"Unexpected status code: {result['status_code']}")
        # Accept all success status codes (2xx)
        self.assertTrue(200 <= result["status_code"] < 300, f"Status code {result['status_code']} is not a success code")
        
        # Wait for creation to complete
        time.sleep(1)
    
    def test_2_read(self):
        """Test reading a thing from Ditto"""
        
        # First create the thing to ensure it exists
                # Call create method with real data
        result = self.controller.create_in_ditto(
            json.dumps(self.test_payload), 
            self.test_toeid, 
            self.test2_level
        )
        
        # Call read method
        result = self.controller.read_item(self.test_toeid, self.test2_level)
        
        # Print and log the result
        print(f"READ Result: {result}")
        logger.info(f"READ Integration Test Result: {result}")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertTrue("attributes" in result)
        self.assertEqual(result["attributes"]["bomFormat"], "CycloneDX")
    
    def test_3_update(self):
        """Test updating a thing in Ditto"""
        
        # First create the thing to ensure it exists
                # Call create method with real data
        result = self.controller.create_in_ditto(
            json.dumps(self.test_payload), 
            self.test_toeid, 
            self.test3_level
        )
        
        # Update the payload
        updated_payload = self.test_payload.copy()
        updated_payload["attributes"]["specVersion"] = "1.7"
        
        # Call update method
        result = self.controller.update_item(
            self.test_toeid, 
            self.test3_level, 
            updated_payload
        )
        
        # Print and log the result
        print(f"UPDATE Result: {result}")
        logger.info(f"UPDATE Integration Test Result: {result}")
        
        # Assertions
        self.assertTrue("status_code" in result, "Result does not contain 'status_code'")
        self.assertEqual(result["status_code"], 204)  # Update returns 204 No Content
        self.assertEqual(result["status_code"], 204)  # Update returns 204 No Content
        
        # Verify the update by reading
        time.sleep(1)  # Wait for update to complete
        read_result = self.controller.read_item(self.test_toeid, self.test3_level)
        self.assertEqual(read_result["attributes"]["specVersion"], "1.7")
    
    def test_4_delete(self):
        """Test deleting a thing from Ditto"""
        
        # First create the thing to ensure it exists
                # Call create method with real data
        result = self.controller.create_in_ditto(
            json.dumps(self.test_payload), 
            self.test_toeid, 
            self.test4_level
        )
        
        # Call delete method
        result = self.controller.delete_item(self.test_toeid, self.test4_level)
        
        # Print and log the result
        print(f"DELETE Result: {result}")
        logger.info(f"DELETE Integration Test Result: {result}")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 204)
        
        # Verify deletion by trying to read (should return None or fail)
        time.sleep(1)  # Wait for deletion to complete
        read_result = self.controller.read_item(self.test_toeid, self.test4_level)
        self.assertIsNone(read_result)


if __name__ == '__main__':
    print("Running integration tests with real Ditto server...")
    
    # Create an interactive menu for testing
    while True:
        print("\n" + "="*50)
        print("=== Controller Integration Test Menu ===")
        print("="*50)
        print("1. Run Create Test")
        print("2. Run Read Test")
        print("3. Run Update Test")
        print("4. Run Delete Test")
        print("5. Run All Tests")
        print("q. Quit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-5 or q): ").lower()
        
        if choice == 'q':
            print("Exiting test runner.")
            break
        
        test_suite = unittest.TestSuite()
        runner = unittest.TextTestRunner(verbosity=2)
        
        if choice == '1':
            test_suite.addTest(TestControllerIntegration('test_1_create'))
        elif choice == '2':
            test_suite.addTest(TestControllerIntegration('test_2_read'))
        elif choice == '3':
            test_suite.addTest(TestControllerIntegration('test_3_update'))
        elif choice == '4':
            test_suite.addTest(TestControllerIntegration('test_4_delete'))
        elif choice == '5':
            test_suite.addTest(TestControllerIntegration('test_1_create'))
            test_suite.addTest(TestControllerIntegration('test_2_read'))
            test_suite.addTest(TestControllerIntegration('test_3_update'))
            test_suite.addTest(TestControllerIntegration('test_4_delete'))
        else:
            print("Invalid choice. Please select a valid option.")
            continue
        
        runner.run(test_suite)