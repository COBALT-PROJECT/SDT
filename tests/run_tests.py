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
