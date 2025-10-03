-- Monstera Metrics Framework - Demo Queries
-- Run these queries after `dbt seed && dbt run` to see your metrics in action

-- ==============================================================================
-- OVERALL VIEW DASHBOARD - Big Number Tiles
-- ==============================================================================

-- Current MAU (Monthly Active Users)
SELECT
    users_active_monthly as current_mau,
    metric_date
FROM gold.gold_users_active_monthly
WHERE is_current_day = true;

-- Current DAU would come from a similar model (not yet built)
-- For demo, show approximate from recent activity
SELECT COUNT(DISTINCT entity_id) as approximate_dau
FROM bronze.bronze_events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '1 day'
    AND entity_type = 'user'
    AND is_qualifying_event = true;

-- Active Accounts (with healthy engagement)
SELECT COUNT(*) as active_accounts
FROM silver.silver_account_current_state
WHERE current_state IN ('active', 'expanding');

-- Total MRR (Monthly Recurring Revenue)
SELECT
    SUM(monthly_recurring_revenue) as total_mrr,
    ROUND(AVG(health_score), 1) as avg_account_health
FROM silver.silver_account_current_state
WHERE current_state NOT IN ('churned', 'trial');

-- ==============================================================================
-- USER LIFECYCLE STATE DISTRIBUTION
-- ==============================================================================

SELECT
    platform_state,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct_of_total,
    ROUND(AVG(days_since_signup), 0) as avg_days_since_signup,
    ROUND(AVG(total_qualifying_events), 1) as avg_qualifying_events
FROM silver.silver_user_current_state
GROUP BY platform_state
ORDER BY user_count DESC;

-- ==============================================================================
-- ACCOUNT HEALTH DASHBOARD
-- ==============================================================================

-- Account state distribution with key metrics
SELECT
    current_state,
    COUNT(*) as account_count,
    ROUND(AVG(health_score), 1) as avg_health_score,
    ROUND(AVG(seat_utilization_pct), 1) as avg_seat_utilization,
    SUM(total_seats) as total_seats,
    SUM(active_seats) as total_active_seats,
    SUM(monthly_recurring_revenue) as total_mrr,
    ROUND(AVG(days_to_renewal), 0) as avg_days_to_renewal
FROM silver.silver_account_current_state
GROUP BY current_state
ORDER BY
    CASE current_state
        WHEN 'expanding' THEN 1
        WHEN 'active' THEN 2
        WHEN 'new_paid' THEN 3
        WHEN 'trial' THEN 4
        WHEN 'at_risk' THEN 5
        WHEN 'contracting' THEN 6
        WHEN 'churned' THEN 7
    END;

-- Accounts needing attention (At-Risk)
SELECT
    account_name,
    health_score,
    seat_utilization_pct,
    active_seats || '/' || total_seats as seat_usage,
    monthly_recurring_revenue as mrr,
    days_to_renewal,
    CASE
        WHEN health_score < 30 THEN 'Critical'
        WHEN health_score < 50 THEN 'High Risk'
        ELSE 'Monitor'
    END as risk_level
FROM silver.silver_account_current_state
WHERE current_state = 'at_risk'
ORDER BY health_score ASC;

-- ==============================================================================
-- PRODUCT ADOPTION METRICS
-- ==============================================================================

-- Product adoption overview (Product-level only, not features)
SELECT
    p.product_name,
    COUNT(DISTINCT ups.user_id) as total_users,
    COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END) as users_tried,
    COUNT(DISTINCT CASE WHEN ups.current_state = 'active_in_product' THEN ups.user_id END) as users_active,
    COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) as users_activated,
    -- Activation rate: activated / tried
    ROUND(
        COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END), 0)
    , 1) as activation_rate_pct,
    -- Adoption rate: tried / total
    ROUND(
        COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT ups.user_id), 0)
    , 1) as adoption_rate_pct
FROM silver.silver_user_product_states ups
JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
WHERE p.tier = 'product'
GROUP BY p.product_name
ORDER BY users_active DESC;

-- Product-specific state distribution
SELECT
    p.product_name,
    ups.current_state,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY p.product_name), 1) as pct_of_product_users
FROM silver.silver_user_product_states ups
JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
WHERE p.tier = 'product'
GROUP BY p.product_name, ups.current_state
ORDER BY p.product_name, user_count DESC;

-- ==============================================================================
-- MULTI-PRODUCT ADOPTION (Cross-Product Analytics)
-- ==============================================================================

-- How many products are users active in?
SELECT
    product_count,
    user_count,
    ROUND(user_count * 100.0 / SUM(user_count) OVER (), 1) as pct_of_users
FROM (
    SELECT
        COUNT(DISTINCT product_id) FILTER (WHERE current_state = 'active_in_product') as product_count,
        COUNT(DISTINCT user_id) as user_count
    FROM silver.silver_user_product_states
    GROUP BY 1
)
ORDER BY product_count DESC;

-- Product adoption sequences (which products are adopted together?)
WITH user_products AS (
    SELECT
        user_id,
        ARRAY_AGG(p.product_name ORDER BY ups.first_access_at) as product_sequence
    FROM silver.silver_user_product_states ups
    JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
    WHERE p.tier = 'product'
        AND ups.current_state != 'never_adopted'
    GROUP BY user_id
)
SELECT
    product_sequence,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct_of_users
FROM user_products
GROUP BY product_sequence
ORDER BY user_count DESC
LIMIT 10;

-- ==============================================================================
-- EVENT ANALYTICS
-- ==============================================================================

-- Event volume by product
SELECT
    p.product_name,
    COUNT(*) as total_events,
    COUNT(DISTINCT e.entity_id) as unique_users,
    COUNT(DISTINCT CASE WHEN e.is_qualifying_event THEN e.event_id END) as qualifying_events,
    COUNT(DISTINCT CASE WHEN e.is_activation_event THEN e.event_id END) as activation_events,
    ROUND(AVG(CASE WHEN e.is_qualifying_event THEN 1.0 ELSE 0.0 END) * 100, 1) as pct_qualifying,
    MIN(e.event_timestamp) as first_event,
    MAX(e.event_timestamp) as last_event
FROM bronze.bronze_events e
LEFT JOIN bronze.bronze_product_catalog p ON e.product_id = p.product_id
WHERE p.tier = 'product' OR e.product_id IS NULL
GROUP BY p.product_name
ORDER BY total_events DESC;

-- Most common events
SELECT
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT entity_id) as unique_users,
    ROUND(AVG(CASE WHEN is_qualifying_event THEN 1.0 ELSE 0.0 END) * 100, 1) as pct_qualifying
FROM bronze.bronze_events
WHERE entity_type = 'user'
GROUP BY event_type
ORDER BY event_count DESC
LIMIT 15;

-- ==============================================================================
-- TREND ANALYSIS (MAU over time)
-- ==============================================================================

-- MAU trend - Last 90 days
SELECT
    metric_date,
    users_active_monthly as mau_total,
    users_active_monthly_us as mau_us,
    users_active_monthly_uk as mau_uk,
    users_active_monthly_enterprise as mau_enterprise,
    users_active_monthly_professional as mau_professional
FROM gold.gold_users_active_monthly
WHERE is_last_90_days = true
ORDER BY metric_date DESC;

-- ==============================================================================
-- COHORT ANALYSIS (By Signup Month)
-- ==============================================================================

-- User state distribution by signup cohort
SELECT
    DATE_TRUNC('month', user_created_at) as signup_month,
    platform_state,
    COUNT(*) as user_count,
    ROUND(AVG(days_since_signup), 0) as avg_days_since_signup
FROM silver.silver_user_current_state
GROUP BY signup_month, platform_state
ORDER BY signup_month DESC, user_count DESC;

-- ==============================================================================
-- SEGMENTATION PREVIEW (Country, Plan Type)
-- ==============================================================================

-- User state by country
SELECT
    u.country,
    s.platform_state,
    COUNT(*) as user_count
FROM silver.silver_user_current_state s
JOIN bronze.bronze_users u ON s.user_id = u.user_id
GROUP BY u.country, s.platform_state
ORDER BY u.country, user_count DESC;

-- User state by plan type
SELECT
    u.plan_type,
    s.platform_state,
    COUNT(*) as user_count,
    ROUND(AVG(s.total_qualifying_events), 1) as avg_qualifying_events
FROM silver.silver_user_current_state s
JOIN bronze.bronze_users u ON s.user_id = u.user_id
GROUP BY u.plan_type, s.platform_state
ORDER BY u.plan_type, user_count DESC;

-- ==============================================================================
-- EXPORT QUERIES (for CSV/Spreadsheet demos)
-- ==============================================================================

-- Export 1: User State Summary for Pie Chart
-- COPY (
SELECT
    platform_state as "User State",
    COUNT(*) as "Count",
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as "Percentage"
FROM silver.silver_user_current_state
GROUP BY platform_state
-- ) TO 'user_states_pie.csv' (HEADER, DELIMITER ',');

-- Export 2: MAU Trend for Line Chart
-- COPY (
SELECT
    metric_date as "Date",
    users_active_monthly as "Total MAU",
    users_active_monthly_enterprise as "Enterprise MAU",
    users_active_monthly_professional as "Professional MAU"
FROM gold.gold_users_active_monthly
WHERE is_last_90_days = true
ORDER BY metric_date
-- ) TO 'mau_trend.csv' (HEADER, DELIMITER ',');

-- Export 3: Account Health for Dashboard
-- COPY (
SELECT
    current_state as "Account State",
    COUNT(*) as "Count",
    ROUND(AVG(health_score), 1) as "Avg Health Score",
    SUM(monthly_recurring_revenue) as "Total MRR"
FROM silver.silver_account_current_state
GROUP BY current_state
-- ) TO 'account_health.csv' (HEADER, DELIMITER ',');

-- Export 4: Product Adoption for Bar Chart
-- COPY (
SELECT
    p.product_name as "Product",
    COUNT(DISTINCT CASE WHEN ups.current_state = 'active_in_product' THEN ups.user_id END) as "Active Users",
    COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) as "Activated Users"
FROM silver.silver_user_product_states ups
JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
WHERE p.tier = 'product'
GROUP BY p.product_name
ORDER BY "Active Users" DESC
-- ) TO 'product_adoption.csv' (HEADER, DELIMITER ',');
