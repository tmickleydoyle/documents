# Monstera Metrics Demo - Quickstart Guide

This guide will help you run the Monstera metrics framework locally and view sample metrics/dashboards.

## Prerequisites

- Python 3.8+ installed
- PostgreSQL or DuckDB (we'll use DuckDB for simplest setup)
- Basic command line knowledge

## Option 1: DuckDB Setup (Recommended - Fastest)

DuckDB is an in-memory database perfect for demos - no server setup required!

### Step 1: Install Dependencies

```bash
cd /Users/tmickleydoyle/Repos/documents/monstera_dbt_model

# Create virtual environment (if not already created)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dbt-duckdb
pip install dbt-duckdb
```

### Step 2: Configure Profile

The `profiles.yml` file should already be set up for DuckDB. Verify it looks like this:

```yaml
monstera_metrics:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: monstera_demo.duckdb
      threads: 4
```

### Step 3: Install dbt Packages

```bash
dbt deps
```

### Step 4: Load Seed Data

```bash
dbt seed
```

This will load all the mock data (accounts, users, products, events) into DuckDB.

### Step 5: Run Models

```bash
# Run all models
dbt run

# Or run specific layers
dbt run --select bronze.*
dbt run --select silver.*
dbt run --select gold.*
```

### Step 6: Run Tests

```bash
dbt test
```

### Step 7: View the Data

You can query the DuckDB database directly:

```bash
# Install DuckDB CLI (optional)
brew install duckdb  # macOS
# or download from https://duckdb.org/

# Query the database
duckdb monstera_demo.duckdb

# Then run SQL queries:
SELECT * FROM bronze.seed_users LIMIT 10;
SELECT * FROM silver.silver_user_current_state;
SELECT * FROM gold.gold_users_active_monthly ORDER BY metric_date DESC LIMIT 30;
```

## Option 2: PostgreSQL Setup

If you prefer PostgreSQL:

### Step 1: Install PostgreSQL

```bash
# macOS
brew install postgresql
brew services start postgresql

# Create database
createdb monstera_demo
```

### Step 2: Update profiles.yml

```yaml
monstera_metrics:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: your_username
      password: your_password
      database: monstera_demo
      schema: bronze
      threads: 4
```

### Step 3: Run dbt

```bash
dbt deps
dbt seed
dbt run
dbt test
```

## Viewing Metrics - SQL Queries

Once you've run the models, here are some useful queries to demo the metrics:

### User Lifecycle States

```sql
-- Current user state distribution
SELECT
    platform_state,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM silver.silver_user_current_state
GROUP BY platform_state
ORDER BY user_count DESC;

-- Users by state and days since signup
SELECT
    platform_state,
    ROUND(AVG(days_since_signup), 1) as avg_days_since_signup,
    COUNT(*) as user_count
FROM silver.silver_user_current_state
GROUP BY platform_state
ORDER BY avg_days_since_signup;
```

### Product Adoption

```sql
-- Product adoption overview
SELECT
    p.product_name,
    COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END) as users_tried,
    COUNT(DISTINCT CASE WHEN ups.current_state = 'active_in_product' THEN ups.user_id END) as users_active,
    COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) as users_activated,
    ROUND(COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) * 100.0 /
          NULLIF(COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END), 0), 2) as activation_rate_pct
FROM silver.silver_user_product_states ups
JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
WHERE p.tier = 'product'
GROUP BY p.product_name
ORDER BY users_active DESC;

-- Multi-product adoption
SELECT
    COUNT(DISTINCT product_id) FILTER (WHERE current_state = 'active_in_product') as products_active,
    COUNT(DISTINCT user_id) as user_count
FROM silver.silver_user_product_states
GROUP BY 1
ORDER BY 1 DESC;
```

### Account Health

```sql
-- Account state distribution
SELECT
    current_state,
    COUNT(*) as account_count,
    ROUND(AVG(health_score), 1) as avg_health_score,
    ROUND(AVG(seat_utilization_pct), 1) as avg_seat_utilization,
    SUM(monthly_recurring_revenue) as total_mrr
FROM silver.silver_account_current_state
GROUP BY current_state
ORDER BY total_mrr DESC;

-- At-risk accounts detail
SELECT
    account_name,
    health_score,
    seat_utilization_pct,
    active_seats || '/' || total_seats as seat_usage,
    monthly_recurring_revenue,
    days_to_renewal
FROM silver.silver_account_current_state
WHERE current_state = 'at_risk'
ORDER BY health_score ASC;
```

### Monthly Active Users (MAU) Trend

```sql
-- MAU over time
SELECT
    metric_date,
    users_active_monthly as mau,
    users_active_monthly_us,
    users_active_monthly_uk,
    users_active_monthly_enterprise,
    users_active_monthly_professional
FROM gold.gold_users_active_monthly
WHERE is_last_90_days = true
ORDER BY metric_date DESC
LIMIT 30;
```

### Events by Product

```sql
-- Event volume by product
SELECT
    p.product_name,
    COUNT(*) as total_events,
    COUNT(DISTINCT entity_id) as unique_users,
    COUNT(DISTINCT CASE WHEN is_qualifying_event THEN event_id END) as qualifying_events,
    COUNT(DISTINCT CASE WHEN is_activation_event THEN event_id END) as activation_events
FROM bronze.bronze_events e
JOIN bronze.bronze_product_catalog p ON e.product_id = p.product_id
WHERE p.tier = 'product'
GROUP BY p.product_name
ORDER BY total_events DESC;
```

## Option 3: Export to CSV for Spreadsheet Demo

If you want to create charts in Excel/Google Sheets:

```bash
# After running dbt, export key metrics to CSV

# Using DuckDB CLI
duckdb monstera_demo.duckdb << EOF
COPY (SELECT * FROM gold.gold_users_active_monthly ORDER BY metric_date DESC LIMIT 90)
TO 'exports/mau_trend.csv' (HEADER, DELIMITER ',');

COPY (SELECT platform_state, COUNT(*) as count FROM silver.silver_user_current_state GROUP BY 1)
TO 'exports/user_states.csv' (HEADER, DELIMITER ',');

COPY (SELECT current_state, COUNT(*) as count, AVG(health_score) as avg_health
      FROM silver.silver_account_current_state GROUP BY 1)
TO 'exports/account_states.csv' (HEADER, DELIMITER ',');
EOF
```

## Option 4: Use Evidence.dev for Dashboard (Advanced)

Evidence.dev is a code-based BI tool perfect for demos:

```bash
# Install Evidence
npm install -g @evidence-dev/evidence

# Create Evidence project
npx degit evidence-dev/template monstera-dashboard
cd monstera-dashboard

# Update sources/connection.yaml to point to your DuckDB file
# Then run
npm run dev
```

Create pages in Evidence using the SQL queries above to build interactive dashboards.

## Option 5: Use Metabase (Visual Dashboard)

Metabase is open-source and has a nice UI:

```bash
# Run Metabase with Docker
docker run -d -p 3000:3000 --name metabase metabase/metabase

# Open http://localhost:3000
# Connect to your DuckDB or PostgreSQL database
# Create dashboards using the SQL queries above
```

## Sample Dashboard Structure

Based on Monstera framework, create these 3 dashboard types:

### 1. Overall View Dashboard
**Big Number Tiles:**
- Total Users Active Monthly (current MAU)
- Users Active Daily (current DAU)
- Accounts Active Monthly
- Total MRR

**Charts (Last 90 Days):**
- MAU Trend (line chart)
- User State Distribution (pie chart)
- Account Health Distribution (bar chart)

### 2. Segment View Dashboard
**Charts (Last 18 Months):**
- MAU by Country (stacked area chart)
- MAU by Plan Type (stacked area chart)
- Active Accounts by Subscription Tier (bar chart)
- User State Distribution by Cohort (stacked bar)

### 3. Activity View Dashboard
**Charts (Last 18 Months):**
- Events by Product (line chart)
- Product Adoption Funnel (funnel chart)
- Activation Rate by Product (bar chart)
- Multi-Product Adoption (distribution chart)

## Troubleshooting

### "Relation not found" errors
Make sure you've run `dbt seed` before `dbt run`

### "Database not found"
Check your `profiles.yml` path is correct

### Need more data?
Edit the seed CSV files in `/seeds/` to add more rows, then re-run `dbt seed --full-refresh`

### Want to reset everything?
```bash
rm monstera_demo.duckdb
dbt seed --full-refresh
dbt run --full-refresh
```

## Next Steps

1. Run through this quickstart
2. Query the metrics using the SQL examples above
3. Export to CSV or set up a dashboard tool
4. Customize the seed data to match your use case
5. Share screenshots or live demo with stakeholders

## Example Demo Flow

1. **Show User Lifecycle States** - "Here's how we categorize users: 30% active, 15% new, 25% dormant, 30% churned"
2. **Show Product Adoption** - "Video Editor has 85% activation rate, while Template Library is 60%"
3. **Show Account Health** - "We have 2 at-risk accounts worth $3K MRR that need attention"
4. **Show Trends** - "MAU has grown 15% over last 90 days, mainly from professional tier"
5. **Show Cross-Product** - "Users who adopt Video Editor + Template Library have 2x retention"

This demonstrates the Monstera framework's value: standardized metrics, clear user states, product-level insights, and actionable account health scoring.
