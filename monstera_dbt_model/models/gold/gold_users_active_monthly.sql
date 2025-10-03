{{
  config(
    materialized='table',
    description='Users Active Monthly - Monthly active users metric following Monstera naming conventions'
  )
}}

-- Gold layer: Users Active Monthly (MAU)
-- Metric Name Format: [Entity Type] [Action/State] [Time Period]
-- Example from Monstera framework: "Users Active Monthly"
--
-- This model calculates Monthly Active Users following the Monstera framework:
-- - Entity Type: Users
-- - Action/State: Active (performed qualifying events)
-- - Time Period: Monthly (last 30 days)

WITH date_spine AS (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2023-01-01' as date)",
        end_date="cast('2025-12-31' as date)"
    ) }}
),

daily_active_users AS (
    SELECT
        DATE_TRUNC('day', e.event_timestamp) as event_date,
        COUNT(DISTINCT e.entity_id) as daily_active_users,
        COUNT(DISTINCT CASE WHEN u.country = 'US' THEN e.entity_id END) as dau_us,
        COUNT(DISTINCT CASE WHEN u.country = 'UK' THEN e.entity_id END) as dau_uk,
        COUNT(DISTINCT CASE WHEN u.country = 'CA' THEN e.entity_id END) as dau_ca,
        COUNT(DISTINCT CASE WHEN u.plan_type = 'enterprise' THEN e.entity_id END) as dau_enterprise,
        COUNT(DISTINCT CASE WHEN u.plan_type = 'professional' THEN e.entity_id END) as dau_professional,
        COUNT(DISTINCT CASE WHEN u.plan_type = 'starter' THEN e.entity_id END) as dau_starter
    FROM {{ ref('bronze_events') }} e
    INNER JOIN {{ ref('bronze_users') }} u ON e.entity_id = u.user_id
    WHERE e.entity_type = 'user'
        AND e.is_qualifying_event = true
    GROUP BY 1
),

monthly_active_users AS (
    SELECT
        d.date_day as metric_date,

        -- 30-day rolling window for MAU
        COUNT(DISTINCT CASE
            WHEN dau.event_date BETWEEN d.date_day - INTERVAL '29 days' AND d.date_day
            THEN dau.event_date || '-' || dau.daily_active_users
        END) as mau_30day,

        -- Country segments
        COUNT(DISTINCT CASE
            WHEN dau.event_date BETWEEN d.date_day - INTERVAL '29 days' AND d.date_day
            THEN dau.dau_us
        END) as mau_us,
        COUNT(DISTINCT CASE
            WHEN dau.event_date BETWEEN d.date_day - INTERVAL '29 days' AND d.date_day
            THEN dau.dau_uk
        END) as mau_uk,

        -- Plan type segments
        COUNT(DISTINCT CASE
            WHEN dau.event_date BETWEEN d.date_day - INTERVAL '29 days' AND d.date_day
            THEN dau.dau_enterprise
        END) as mau_enterprise,
        COUNT(DISTINCT CASE
            WHEN dau.event_date BETWEEN d.date_day - INTERVAL '29 days' AND d.date_day
            THEN dau.dau_professional
        END) as mau_professional

    FROM date_spine d
    LEFT JOIN daily_active_users dau
        ON dau.event_date BETWEEN d.date_day - INTERVAL '29 days' AND d.date_day
    WHERE d.date_day >= '2023-01-01'
    GROUP BY 1
)

SELECT
    metric_date,
    mau_30day as users_active_monthly,
    mau_us as users_active_monthly_us,
    mau_uk as users_active_monthly_uk,
    mau_enterprise as users_active_monthly_enterprise,
    mau_professional as users_active_monthly_professional,
    metric_date = CURRENT_DATE as is_current_day,
    metric_date >= CURRENT_DATE - INTERVAL '90 days' as is_last_90_days
FROM monthly_active_users
ORDER BY metric_date DESC
