#!/bin/bash

# Export Demo Data to CSV
# Creates CSV files that can be used in spreadsheets or BI tools

set -e

echo "Exporting Monstera metrics to CSV..."

# Create exports directory
mkdir -p exports

# Export 1: User State Distribution (for pie chart)
echo "Exporting user state distribution..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        platform_state as "User State",
        COUNT(*) as "Count",
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as "Percentage"
    FROM silver.silver_user_current_state
    GROUP BY platform_state
    ORDER BY "Count" DESC
) TO 'exports/user_states.csv' (HEADER, DELIMITER ',');
EOF

# Export 2: MAU Trend (for line chart)
echo "Exporting MAU trend..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        metric_date as "Date",
        users_active_monthly as "Total MAU",
        users_active_monthly_enterprise as "Enterprise MAU",
        users_active_monthly_professional as "Professional MAU"
    FROM gold.gold_users_active_monthly
    WHERE is_last_90_days = true
    ORDER BY metric_date
) TO 'exports/mau_trend.csv' (HEADER, DELIMITER ',');
EOF

# Export 3: Account Health (for dashboard)
echo "Exporting account health metrics..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        current_state as "Account State",
        COUNT(*) as "Count",
        ROUND(AVG(health_score), 1) as "Avg Health Score",
        ROUND(AVG(seat_utilization_pct), 1) as "Avg Seat Utilization %",
        SUM(monthly_recurring_revenue) as "Total MRR"
    FROM silver.silver_account_current_state
    GROUP BY current_state
    ORDER BY "Total MRR" DESC
) TO 'exports/account_health.csv' (HEADER, DELIMITER ',');
EOF

# Export 4: Product Adoption (for bar chart)
echo "Exporting product adoption metrics..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        p.product_name as "Product",
        COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END) as "Users Tried",
        COUNT(DISTINCT CASE WHEN ups.current_state = 'active_in_product' THEN ups.user_id END) as "Users Active",
        COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) as "Users Activated",
        ROUND(
            COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) * 100.0 /
            NULLIF(COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END), 0)
        , 1) as "Activation Rate %"
    FROM silver.silver_user_product_states ups
    JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
    WHERE p.tier = 'product'
    GROUP BY p.product_name
    ORDER BY "Users Active" DESC
) TO 'exports/product_adoption.csv' (HEADER, DELIMITER ',');
EOF

# Export 5: Product State Distribution (for stacked bar)
echo "Exporting product state distribution..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        p.product_name as "Product",
        ups.current_state as "State",
        COUNT(*) as "User Count"
    FROM silver.silver_user_product_states ups
    JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
    WHERE p.tier = 'product'
    GROUP BY p.product_name, ups.current_state
    ORDER BY p.product_name, "User Count" DESC
) TO 'exports/product_states.csv' (HEADER, DELIMITER ',');
EOF

# Export 6: At-Risk Accounts Detail
echo "Exporting at-risk accounts..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        account_name as "Account",
        health_score as "Health Score",
        seat_utilization_pct as "Seat Utilization %",
        active_seats || '/' || total_seats as "Seat Usage",
        monthly_recurring_revenue as "MRR",
        days_to_renewal as "Days to Renewal"
    FROM silver.silver_account_current_state
    WHERE current_state = 'at_risk'
    ORDER BY health_score ASC
) TO 'exports/at_risk_accounts.csv' (HEADER, DELIMITER ',');
EOF

# Export 7: Event Summary
echo "Exporting event summary..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        COALESCE(p.product_name, 'Platform') as "Product",
        COUNT(*) as "Total Events",
        COUNT(DISTINCT e.entity_id) as "Unique Users",
        COUNT(DISTINCT CASE WHEN e.is_qualifying_event THEN e.event_id END) as "Qualifying Events",
        ROUND(AVG(CASE WHEN e.is_qualifying_event THEN 1.0 ELSE 0.0 END) * 100, 1) as "% Qualifying"
    FROM bronze.bronze_events e
    LEFT JOIN bronze.bronze_product_catalog p ON e.product_id = p.product_id AND p.tier = 'product'
    WHERE e.entity_type = 'user'
    GROUP BY COALESCE(p.product_name, 'Platform')
    ORDER BY "Total Events" DESC
) TO 'exports/event_summary.csv' (HEADER, DELIMITER ',');
EOF

# Export 8: Multi-Product Adoption
echo "Exporting multi-product adoption..."
duckdb monstera_demo.duckdb << EOF
COPY (
    SELECT
        product_count as "# Products Active",
        user_count as "User Count",
        ROUND(user_count * 100.0 / SUM(user_count) OVER (), 1) as "% of Users"
    FROM (
        SELECT
            COUNT(DISTINCT product_id) FILTER (WHERE current_state = 'active_in_product') as product_count,
            COUNT(DISTINCT user_id) as user_count
        FROM silver.silver_user_product_states
        GROUP BY 1
    )
    ORDER BY product_count DESC
) TO 'exports/multi_product_adoption.csv' (HEADER, DELIMITER ',');
EOF

echo ""
echo "✅ Export complete!"
echo ""
echo "CSV files created in ./exports/:"
ls -lh exports/*.csv | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "You can now:"
echo "1. Open these in Excel/Google Sheets to create charts"
echo "2. Import into a BI tool (Tableau, Metabase, etc.)"
echo "3. Share with stakeholders as data samples"
