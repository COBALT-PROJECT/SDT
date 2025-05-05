import unittest
import sys
import os
import time
import datetime
import json
import webbrowser  # Added for opening the report
from unittest import TextTestRunner, TestLoader
from unit.test_controller import TestController
from unit.test_evidence_provider import TestEvidenceProvider
from integration.test_api_endpoints import TestAPIEndpoints

class HTMLTestRunner:
    def __init__(self, output_file):
        self.output_file = output_file
        self.test_results = {
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "duration": None,
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "error_tests": 0,
            "test_cases": []
        }
        
    def run(self, test_suite):
        loader = TestLoader()
        runner = TextTestRunner(verbosity=2)
        
        start_time = time.time()
        
        # Run each test class separately to capture results
        for test_class in test_suite:
            test_case = {
                "class_name": test_class.__name__,
                "tests": []
            }
            
            suite = loader.loadTestsFromTestCase(test_class)
            self.test_results["total_tests"] += suite.countTestCases()
            
            for test in suite:
                test_name = test._testMethodName
                test_result = {
                    "name": test_name,
                    "status": "Passed",
                    "error": None,
                    "execution_time": 0
                }
                
                start_test_time = time.time()
                try:
                    test.setUp()
                    getattr(test, test_name)()
                    self.test_results["successful_tests"] += 1
                except AssertionError as e:
                    test_result["status"] = "Failed"
                    test_result["error"] = str(e)
                    self.test_results["failed_tests"] += 1
                except Exception as e:
                    test_result["status"] = "Error"
                    test_result["error"] = str(e)
                    self.test_results["error_tests"] += 1
                finally:
                    try:
                        test.tearDown()
                    except:
                        pass
                
                test_result["execution_time"] = time.time() - start_test_time
                test_case["tests"].append(test_result)
            
            self.test_results["test_cases"].append(test_case)
        
        end_time = time.time()
        self.test_results["duration"] = end_time - start_time
        self.test_results["end_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._generate_report()
        
        return self.test_results
    
    def _generate_report(self):
        # Save JSON report
        with open(f"{self.output_file}.json", "w") as f:
            json.dump(self.test_results, f, indent=4)
        
        # Generate HTML report
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SDT Service Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .summary {{ margin: 20px 0; }}
                .test-case {{ margin-bottom: 30px; }}
                .test {{ margin: 10px 0; padding: 10px; border-bottom: 1px solid #eee; }}
                .passed {{ background-color: #dff0d8; }}
                .failed {{ background-color: #f2dede; }}
                .error {{ background-color: #fcf8e3; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SDT Service Test Report</h1>
                <p>Start Time: {start_time}</p>
                <p>End Time: {end_time}</p>
                <p>Duration: {duration:.2f} seconds</p>
            </div>
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr>
                        <th>Total Tests</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Errors</th>
                    </tr>
                    <tr>
                        <td>{total_tests}</td>
                        <td>{successful_tests}</td>
                        <td>{failed_tests}</td>
                        <td>{error_tests}</td>
                    </tr>
                </table>
            </div>
        """.format(**self.test_results)
        
        for test_case in self.test_results["test_cases"]:
            html += f"""
            <div class="test-case">
                <h2>{test_case['class_name']}</h2>
            """
            
            for test in test_case["tests"]:
                status_class = "passed" if test["status"] == "Passed" else "failed" if test["status"] == "Failed" else "error"
                html += f"""
                <div class="test {status_class}">
                    <h3>{test['name']}</h3>
                    <p>Status: {test['status']}</p>
                    <p>Execution Time: {test['execution_time']:.2f} seconds</p>
                """
                
                if test["error"]:
                    html += f"""
                    <div class="error-details">
                        <p>Error: {test['error']}</p>
                    </div>
                    """
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        with open(f"{self.output_file}.html", "w") as f:
            f.write(html)

def run_all_tests():
    test_suite = [
        TestController,
        TestEvidenceProvider,
        TestAPIEndpoints
    ]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_report_{timestamp}")
    
    # Run tests and generate report
    runner = HTMLTestRunner(output_file)
    results = runner.run(test_suite)
    
    print(f"\nTest Report Generated: {output_file}.html")
    print(f"JSON Results: {output_file}.json")
    
    # Automatically open the HTML report in default browser
    try:
        html_report_path = f"{output_file}.html"
        # Convert to file:// URL format for browser compatibility
        file_url = f"file://{os.path.abspath(html_report_path)}"
        print(f"Opening report in browser: {file_url}")
        webbrowser.open(file_url)
        print("Report opened in default web browser")
    except Exception as e:
        print(f"Could not open report automatically: {str(e)}")
    
    # Return non-zero exit code if tests failed
    if results["failed_tests"] > 0 or results["error_tests"] > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(run_all_tests())