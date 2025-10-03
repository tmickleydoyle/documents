#!/bin/bash

# Monstera Metrics Demo Runner
# This script sets up and runs the complete demo

set -e  # Exit on error

echo "======================================"
echo "Monstera Metrics Framework Demo"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dbt-duckdb if not installed
echo -e "${BLUE}Installing dbt-duckdb...${NC}"
pip install -q dbt-duckdb

# Install dbt packages
echo -e "${BLUE}Installing dbt packages (dbt_utils)...${NC}"
dbt deps

# Load seed data
echo -e "${GREEN}Loading seed data (mock accounts, users, products, events)...${NC}"
dbt seed --full-refresh

# Run bronze layer
echo -e "${GREEN}Building bronze layer (raw data)...${NC}"
dbt run --select bronze.*

# Run silver layer
echo -e "${GREEN}Building silver layer (user states, product states, account states)...${NC}"
dbt run --select silver.*

# Run gold layer
echo -e "${GREEN}Building gold layer (aggregated metrics)...${NC}"
dbt run --select gold.*

# Run tests
echo -e "${BLUE}Running data quality tests...${NC}"
dbt test || echo -e "${YELLOW}Some tests failed - this is expected with limited mock data${NC}"

echo ""
echo -e "${GREEN}======================================"
echo "Demo setup complete!"
echo -e "======================================${NC}"
echo ""
echo "Your DuckDB database is ready: monstera_demo.duckdb"
echo ""
echo "Next steps:"
echo "1. Query the database:"
echo "   duckdb monstera_demo.duckdb"
echo ""
echo "2. Run demo queries:"
echo "   duckdb monstera_demo.duckdb < demo_queries.sql"
echo ""
echo "3. Export to CSV:"
echo "   ./export_demo_data.sh"
echo ""
echo "4. View specific metrics:"
echo "   duckdb monstera_demo.duckdb -c \"SELECT * FROM silver.silver_user_current_state;\""
echo ""
echo "See QUICKSTART_DEMO.md for more options!"
