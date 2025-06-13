# Monstera dbt Implementation

This project demonstrates the Monstera Company Metrics Design framework using dbt with a medallion architecture (bronze, silver, gold layers) and PostgreSQL.

## Architecture

### Medallion Layers
- **Bronze (Raw)**: Raw event data as ingested from source systems
- **Silver (Cleaned)**: Cleaned, validated, and enriched event data with entity information
- **Gold (Aggregated)**: Pre-computed metrics and dimensional models for analytics

### Data Model
Based on the Monstera framework with:
- Entity-centric design (users, accounts, projects, videos)
- Event-driven architecture with standardized schema
- Three-tier dashboard structure (Overall, Segment, Activity views)

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL 12+
- dbt-postgres

### 2. Database Setup
```bash
# Start PostgreSQL and create database
createdb monstera_demo

# Run setup script to create sample data
python scripts/setup_sample_data.py
```

### 3. dbt Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure profiles
cp profiles.yml ~/.dbt/profiles.yml

# Run dbt
dbt deps
dbt seed
dbt run
dbt test
```

### 4. View Results
Connect to PostgreSQL and explore the gold layer tables:
- `gold.overall_metrics`
- `gold.segment_metrics`
- `gold.activity_metrics`

## Project Structure

```
monstera_dbt_model/
├── models/
│   ├── bronze/          # Raw event data
│   ├── silver/          # Cleaned and enriched data
│   └── gold/           # Aggregated metrics
├── seeds/              # Sample data files
├── macros/             # dbt macros
├── tests/              # Data quality tests
└── scripts/            # Setup scripts
```

## Key Metrics Implemented

- **Activity Metrics**: User logins, video uploads, comment creation
- **Engagement Metrics**: Session duration, feature usage patterns
- **Outcome Metrics**: User retention, project completion rates

## Event Schema

All events follow the standardized Monstera schema:
```json
{
  "entity_id": "string (required)",
  "entity_type": "string (required)",
  "event_type": "string (required)",
  "timestamp": "ISO 8601 datetime (required)",
  "location": "string (required)",
  "session_id": "string (optional)",
  "metadata": {}
}
```
