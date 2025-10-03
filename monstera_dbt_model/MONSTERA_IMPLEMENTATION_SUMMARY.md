# Monstera DBT Model - Implementation Summary

This document summarizes all updates made to align the monstera_dbt_model with the Monstera Company Metrics Design framework.

## Overview

The monstera_dbt_model has been comprehensively updated to implement the Monstera framework, including:
- User lifecycle states (8 states: new, active, returning, dormant, churned, reactivated, dunning, deleted)
- Product taxonomy and hierarchy (4-tier structure)
- Account-level lifecycle states (9 states for B2B metrics)
- Product-specific user states
- Behavioral segmentation foundations
- Monstera naming conventions throughout

## Changes Made

### 1. Seed Files (Mock Data)

**Created:**
- `seeds/seed_product_catalog.csv` - Product taxonomy with hierarchy
  - 17 products across 3 families (content_creation, collaboration, analytics)
  - Includes products and features with parent relationships

- `seeds/seed_accounts.csv` - Account entity data
  - 10 sample accounts with subscription tiers, seats, MRR
  - Mix of trial and paid accounts
  - Renewal dates and payment information

- `seeds/seed_users.csv` - User entity data
  - 20 sample users across multiple accounts
  - Geographic distribution (US, UK, CA, AU, DE, FR)
  - Acquisition sources and plan types

- `seeds/seed_events.csv` - Event data following Monstera schema
  - 40 sample events across products
  - Includes qualifying events and activation events
  - Product-specific events (video_created, template_selected, etc.)

### 2. Bronze Layer Models (Raw Data)

**Updated `models/bronze/bronze_events.sql`:**
- Added product_id field for product taxonomy
- Added is_qualifying_event boolean (for user state calculations)
- Added is_activation_event boolean (for product activation tracking)
- Enhanced documentation with Monstera schema requirements
- Added timestamp validation (realistic dates only)

**Updated `models/bronze/bronze_accounts.sql`:**
- Changed to B2B account structure
- Fields: subscription_tier, total_seats, MRR, renewal dates
- Removed generic industry fields
- Added trial status tracking

**Updated `models/bronze/bronze_users.sql`:**
- Simplified to core user attributes
- Added user_created_at (for lifecycle calculations)
- Added country, plan_type, acquisition_source (for segmentation)
- Removed unused name fields

**Created `models/bronze/bronze_product_catalog.sql`:**
- Product taxonomy and hierarchy
- 4-tier structure (family/product/feature/sub-feature)
- Parent-child relationships for features
- Active/inactive status tracking

### 3. Silver Layer Models (Business Logic)

**Created `models/silver/silver_user_current_state.sql`:**
- Platform-wide user lifecycle states
- 8 states: new, active, returning, dormant, churned, reactivated, deleted, unknown
- Time-based state definitions:
  - New: 0-30 days from signup
  - Active: Qualifying events within last 30 days
  - Dormant: 31-60 days inactive
  - Churned: 61+ days inactive
- Tracks last qualifying event, days since signup, days since last activity
- State transition timestamps

**Created `models/silver/silver_user_product_states.sql`:**
- Product-specific user lifecycle states
- 6 states: never_adopted, new_to_product, active_in_product, dormant_in_product, churned_from_product, reactivated_in_product
- User-product cartesian join (all users × all active products)
- Tracks first access, activation date, qualifying events per product
- Enables cross-product analysis

**Created `models/silver/silver_account_current_state.sql`:**
- Account-level lifecycle states for B2B
- 9 states: trial, new_paid, active, expanding, at_risk, contracting, churned, reactivated, frozen
- Seat utilization calculations (active users / total seats)
- Account health score (0-100) with weighted components:
  - Seat utilization (25%)
  - Product breadth (25%)
  - Recent activity (25%)
  - Contract status (25%)
- Days to renewal tracking

### 4. Gold Layer Models (Aggregated Metrics)

**Created `models/gold/gold_users_active_monthly.sql`:**
- Monthly Active Users (MAU) following Monstera naming conventions
- Metric Name Format: "Users Active Monthly"
- 30-day rolling window calculation
- Segmentation by:
  - Country (US, UK, CA)
  - Plan type (enterprise, professional, starter)
- 90-day trend tracking for dashboards

**Existing `models/gold/gold_overall_metrics.sql`:**
- Needs update to use new silver layer models
- Should follow Monstera naming: [Entity] [Action] [Time Period]

**Existing `models/gold/gold_segment_metrics.sql`:**
- Needs update for behavioral segmentation framework
- Should include engagement intensity, value realization segments

**Existing `models/gold/gold_activity_metrics.sql`:**
- Needs update for product-specific activity metrics
- Should include workflow completion rates

### 5. Naming Conventions

**Event Naming:**
- Format: `[product_name]_[action]_[object]`
- Examples: `video_created`, `ai_voice_cloning_used`, `template_selected`
- Lowercase with underscores

**Product Naming:**
- Product Names: Title Case ("Video Editor", "Team Workspace")
- Product IDs: snake_case (`video_editor`, `team_workspace`)

**Metric Naming:**
- Format: `[Entity Type] [Action/State] [Time Period] [by Segment]`
- Examples:
  - "Users Active Monthly"
  - "Users Active Monthly by Country"
  - "Videos Created Daily"
  - "Accounts Churned Monthly"

### 6. Data Models Alignment

**User Lifecycle States:**
```sql
user_current_state:
  - user_id (PK)
  - platform_state (new/active/returning/dormant/churned/reactivated/deleted)
  - platform_state_since (timestamp)
  - last_qualifying_event_at (timestamp)
  - total_qualifying_events (integer)
  - days_since_signup (integer)
  - days_since_last_qualifying_event (integer)
  - state_updated_at (timestamp)
```

**Product-Specific States:**
```sql
user_product_states:
  - user_id (FK)
  - product_id (FK)
  - current_state (never_adopted/new_to_product/active_in_product/dormant_in_product/churned_from_product)
  - state_since (timestamp)
  - first_access_at (timestamp)
  - last_qualifying_event_at (timestamp)
  - activation_date (timestamp)
  - total_qualifying_events (integer)
```

**Account States:**
```sql
account_current_state:
  - account_id (PK)
  - current_state (trial/new_paid/active/expanding/at_risk/contracting/churned)
  - subscription_tier
  - total_seats (integer)
  - active_seats (integer)
  - seat_utilization_pct (decimal)
  - health_score (0-100)
  - monthly_recurring_revenue (decimal)
  - contract_renewal_date (date)
  - days_to_renewal (integer)
  - state_since (timestamp)
```

## What Still Needs to Be Done

### High Priority

1. **Update Existing Gold Layer Models:**
   - `gold_overall_metrics.sql` - Use new silver layer models, apply naming conventions
   - `gold_segment_metrics.sql` - Add behavioral segmentation (engagement intensity, value realization)
   - `gold_activity_metrics.sql` - Add product-specific metrics

2. **Create Missing Silver Layer Models:**
   - `silver_behavioral_segments.sql` - Engagement intensity, user journey stage, collaboration behavior
   - `silver_cross_product_analytics.sql` - Product adoption sequences, affinity matrix
   - `silver_user_state_history.sql` - Daily snapshots for historical analysis
   - `silver_account_state_history.sql` - Daily account state snapshots

3. **Create Additional Gold Layer Models:**
   - `gold_users_created_daily.sql` - New user signups
   - `gold_videos_created_daily.sql` - Video creation metrics
   - `gold_accounts_active_monthly.sql` - Monthly active accounts
   - `gold_product_adoption.sql` - Product adoption rates and sequences
   - `gold_retention_cohorts.sql` - Cohort retention analysis

4. **Update Schema YAML Files:**
   - `models/bronze/schema.yml` - Document all fields with Monstera definitions
   - `models/silver/schema.yml` - Add new models with full documentation
   - `models/gold/schema.yml` - Update with Monstera metric catalog format

5. **Sources Configuration:**
   - Update `models/bronze/sources.yml` to reference seed files instead of raw sources
   - Add tests for new fields (product_id, is_qualifying_event, etc.)

### Medium Priority

6. **Create Macro for State Calculations:**
   - `macros/calculate_user_state.sql` - Reusable logic for state determination
   - `macros/calculate_account_health_score.sql` - Health score formula

7. **Add Data Quality Tests:**
   - Test that all events have product_id when applicable
   - Test state transition validity
   - Test that qualifying events are properly flagged
   - Test account seat utilization calculations

8. **Create Documentation:**
   - Update README with Monstera framework overview
   - Document qualifying events per product
   - Document activation criteria per product
   - Add data lineage diagrams

### Low Priority

9. **Performance Optimization:**
   - Add incremental materialization where appropriate
   - Create indexes on state lookup tables
   - Optimize cross-product cartesian joins

10. **Advanced Features:**
    - Predictive churn scoring
    - Product recommendation engine
    - Automated anomaly detection for state distributions

## Key Monstera Framework Elements Implemented

✅ **User Lifecycle States:**
- 8 states with clear definitions and time windows
- Platform-wide state calculation
- Product-specific states
- State transition logic

✅ **Product Taxonomy:**
- 4-tier hierarchy (family/product/feature/sub-feature)
- Product catalog with parent-child relationships
- Product-level event attribution

✅ **Account Lifecycle States:**
- 9 B2B account states
- Seat utilization tracking
- Account health scoring
- Contract renewal tracking

✅ **Event Schema:**
- Standardized event fields
- Qualifying event flagging
- Activation event tracking
- Product attribution

✅ **Naming Conventions:**
- Monstera metric naming format
- Consistent product naming
- Clear event taxonomy

## Next Steps

1. **Run `dbt deps`** to install dbt_utils package
2. **Run `dbt seed`** to load mock data
3. **Run `dbt run`** to build all models
4. **Run `dbt test`** to validate data quality
5. **Update remaining gold layer models** with Monstera conventions
6. **Add comprehensive schema documentation**
7. **Create state history snapshots**
8. **Build behavioral segmentation models**

## References

- Monstera Company Metrics Design document
- User Lifecycle States (Section 5)
- Product Taxonomy and Hierarchy (Section 6)
- Account-Level Lifecycle States (Section 8)
- Behavioral Segmentation Framework (Section 7)
- Metric Naming Conventions (Section 10, Dashboard Design)
