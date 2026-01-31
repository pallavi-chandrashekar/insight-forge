#!/bin/bash

# Query Engine Test Runner
# This script sets up the test environment and runs all tests

set -e  # Exit on error

echo "================================================"
echo "Query Engine - Test Suite"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

# Generate test data
echo -e "${YELLOW}Generating test data...${NC}"
python tests/test_data.py

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${RED}PostgreSQL is not running on localhost:5432${NC}"
    echo "Please start PostgreSQL before running tests"
    exit 1
fi

# Create test database if it doesn't exist
echo -e "${YELLOW}Setting up test database...${NC}"
psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'insightforge_test'" | grep -q 1 || \
    psql -h localhost -U postgres -c "CREATE DATABASE insightforge_test"

# Set test environment variables
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/insightforge_test"
export API_KEY="test-api-key"
export SECRET_KEY="test-secret-key-for-testing-only"

echo ""
echo -e "${GREEN}Running tests...${NC}"
echo "================================================"
echo ""

# Run tests with coverage
pytest tests/ \
    -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    -m "not slow" \
    "$@"

EXIT_CODE=$?

echo ""
echo "================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Coverage report saved to: htmlcov/index.html"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi
echo "================================================"

exit $EXIT_CODE
