#!/bin/bash
# filepath: /home/abdul/DigitalTwin/Cobalt/SDT/SDT/create_test_structure.sh

# Set the base directory
BASE_DIR="/home/abdul/DigitalTwin/Cobalt/SDT/SDT"
cd "${BASE_DIR}"

echo "Creating test directory structure..."

# Create directory structure
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/reports

# Create empty test files
touch tests/conftest.py
touch tests/run_tests.py
touch tests/unit/test_controller.py
touch tests/unit/test_evidence_provider.py
touch tests/unit/test_adapter.py
touch tests/integration/test_api_endpoints.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# Create requirements-test.txt
cat > tests/requirements-test.txt << EOF
pytest>=7.0.0
pytest-cov>=4.0.0
httpx>=0.23.0
EOF

# Create empty init.py files for proper imports
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

echo "Test structure created successfully!"
echo "Directory structure:"
find tests -type d | sort

echo -e "\nCreated files:"
find tests -type f | sort

echo -e "\nTo run tests in the future, execute:"
echo "python tests/run_tests.py"

# Make the script executable
chmod +x "${BASE_DIR}/create_test_structure.sh"