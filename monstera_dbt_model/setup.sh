#!/bin/bash

# Setup script for Monstera dbt demo
# Creates PostgreSQL database and runs the complete pipeline

set -e

echo "🌿 Setting up Monstera dbt Demo..."

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    echo "On macOS with Homebrew: brew services start postgresql"
    exit 1
fi

# Create database if it doesn't exist
echo "📊 Creating database 'monstera_demo'..."
createdb monstera_demo 2>/dev/null || echo "Database 'monstera_demo' already exists"

# Set environment variables for database connection
export POSTGRES_USER=${POSTGRES_USER:-$(whoami)}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-""}

echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "📝 Generating sample data..."
python scripts/setup_sample_data.py

echo "🔧 Setting up dbt..."

# Copy profiles if it doesn't exist in home directory
if [ ! -f ~/.dbt/profiles.yml ]; then
    echo "📋 Copying dbt profiles..."
    mkdir -p ~/.dbt
    cp profiles.yml ~/.dbt/profiles.yml
    echo "✅ Created ~/.dbt/profiles.yml"
else
    echo "📋 dbt profiles already exist"
fi

# Install dbt packages
echo "📦 Installing dbt packages..."
dbt deps

echo "🏗️ Running dbt pipeline..."

# Run dbt models
echo "▶️ Running bronze layer..."
dbt run --select models/bronze

echo "▶️ Running silver layer..."
dbt run --select models/silver

echo "▶️ Running gold layer..."
dbt run --select models/gold

echo "🧪 Running tests..."
dbt test

echo "📊 Pipeline Summary:"
echo "==================="

# Connect to database and show table counts
psql -d monstera_demo -c "
SELECT
    schemaname as schema,
    tablename as table,
    n_tup_ins as rows
FROM pg_stat_user_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
ORDER BY schemaname, tablename;
"

echo ""
echo "🎉 Monstera dbt demo setup complete!"
echo ""
echo "📈 Next steps:"
echo "1. Connect to database: psql -d monstera_demo"
echo "2. Explore gold layer tables:"
echo "   - gold.gold_overall_metrics (Overall View Dashboard)"
echo "   - gold.gold_segment_metrics (Segment View Dashboard)"
echo "   - gold.gold_activity_metrics (Activity View Dashboard)"
echo "3. Run 'dbt docs generate && dbt docs serve' to view documentation"
echo ""
echo "🔍 Sample queries:"
echo "-- Overall metrics for last 30 days"
echo "SELECT * FROM gold.gold_overall_metrics WHERE is_last_90_days = true ORDER BY metric_date DESC LIMIT 30;"
echo ""
echo "-- Top countries by monthly active users"
echo "SELECT country, SUM(monthly_active_users) as total_mau FROM gold.gold_segment_metrics GROUP BY country ORDER BY total_mau DESC LIMIT 10;"
