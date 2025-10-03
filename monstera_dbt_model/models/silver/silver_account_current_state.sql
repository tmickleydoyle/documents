{{
  config(
    materialized='table',
    description='Current account lifecycle states based on Monstera framework'
  )
}}

-- Silver layer: Account Current State
-- Calculates current lifecycle state for each account based on Monstera framework
--
-- Account Lifecycle States (from Monstera framework):
-- - trial: Account in trial period (0-30 days, no paid subscription)
-- - new_paid: Recently converted to paid (0-90 days after first payment)
-- - active: Paid account with healthy engagement (seat utilization >40%)
-- - expanding: Account actively growing (adding users, products, or upgrading)
-- - at_risk: Paid account showing warning signs (low utilization <30%, declining activity)
-- - contracting: Account reducing spend/users but not fully churning
-- - churned: Account cancelled or failed to renew (61+ days since subscription ended)
-- - reactivated: Previously churned account that has resubscribed
-- - frozen: Account paused due to payment issues or voluntary pause

WITH account_activity AS (
    SELECT
        u.account_id,
        COUNT(DISTINCT u.user_id) as total_users,
        COUNT(DISTINCT CASE
            WHEN e.is_qualifying_event
                AND e.event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
            THEN u.user_id
        END) as active_users_30d,
        MAX(CASE WHEN e.is_qualifying_event THEN e.event_timestamp END) as last_qualifying_event_at,
        COUNT(DISTINCT e.product_id) as products_adopted
    FROM {{ ref('bronze_users') }} u
    LEFT JOIN {{ ref('bronze_events') }} e
        ON u.user_id = e.entity_id
        AND e.entity_type = 'user'
    GROUP BY 1
),

account_metrics AS (
    SELECT
        a.account_id,
        a.account_name,
        a.subscription_tier,
        a.total_seats,
        a.account_created_at,
        a.first_paid_at,
        a.contract_renewal_date,
        a.monthly_recurring_revenue,
        a.is_trial,

        aa.total_users,
        aa.active_users_30d,
        aa.last_qualifying_event_at,
        aa.products_adopted,

        -- Calculate seat utilization
        CASE
            WHEN a.total_seats > 0
            THEN ROUND((aa.active_users_30d::DECIMAL / a.total_seats::DECIMAL) * 100, 2)
            ELSE 0
        END as seat_utilization_pct,

        -- Calculate days metrics
        DATEDIFF('day', a.account_created_at, CURRENT_DATE) as days_since_creation,
        COALESCE(DATEDIFF('day', a.first_paid_at, CURRENT_DATE), 0) as days_since_first_paid,
        COALESCE(DATEDIFF('day', a.contract_renewal_date, CURRENT_DATE), 0) as days_to_renewal

    FROM {{ ref('bronze_accounts') }} a
    LEFT JOIN account_activity aa ON a.account_id = aa.account_id
),

account_state_logic AS (
    SELECT
        *,

        -- Determine account state based on Monstera framework rules
        CASE
            -- Trial: In trial period, no paid subscription
            WHEN is_trial = true
                AND first_paid_at IS NULL
                AND days_since_creation <= 30
            THEN 'trial'

            -- Churned trial: Trial expired without conversion
            WHEN is_trial = true
                AND first_paid_at IS NULL
                AND days_since_creation > 30
            THEN 'churned'

            -- New Paid: Recently converted (0-90 days after first payment)
            WHEN first_paid_at IS NOT NULL
                AND days_since_first_paid <= 90
                AND seat_utilization_pct >= 20  -- Some adoption
            THEN 'new_paid'

            -- At-Risk (New Paid with poor adoption)
            WHEN first_paid_at IS NOT NULL
                AND days_since_first_paid <= 90
                AND seat_utilization_pct < 20
            THEN 'at_risk'

            -- Expanding: High utilization and growing
            WHEN first_paid_at IS NOT NULL
                AND seat_utilization_pct >= 70
                AND active_users_30d > (total_seats * 0.6)
            THEN 'expanding'

            -- Active: Healthy engagement (40%+ utilization)
            WHEN first_paid_at IS NOT NULL
                AND seat_utilization_pct >= 40
                AND seat_utilization_pct < 70
            THEN 'active'

            -- Contracting: Declining but still some activity (20-40% utilization)
            WHEN first_paid_at IS NOT NULL
                AND seat_utilization_pct BETWEEN 20 AND 39
                AND days_to_renewal < 0  -- Past renewal, still some activity
            THEN 'contracting'

            -- At-Risk: Low utilization (<30%) or approaching renewal
            WHEN first_paid_at IS NOT NULL
                AND (seat_utilization_pct < 30
                     OR (days_to_renewal BETWEEN -30 AND 0 AND seat_utilization_pct < 50))
            THEN 'at_risk'

            -- Churned: Contract expired or very low activity
            WHEN first_paid_at IS NOT NULL
                AND days_to_renewal < -61
            THEN 'churned'

            ELSE 'unknown'
        END as current_state,

        -- Calculate account health score (0-100)
        LEAST(100, ROUND(
            (seat_utilization_pct * 0.25) +  -- 25% weight on seat utilization
            (LEAST(products_adopted * 20, 100) * 0.25) +  -- 25% weight on product breadth
            (CASE WHEN active_users_30d > 0 THEN 100 ELSE 0 END * 0.25) +  -- 25% weight on recent activity
            (CASE WHEN days_to_renewal >= 0 THEN 100 ELSE 50 END * 0.25)  -- 25% weight on contract status
        , 2)) as health_score

    FROM account_metrics
)

SELECT
    account_id,
    account_name,
    current_state,
    subscription_tier,
    total_seats,
    active_users_30d as active_seats,
    seat_utilization_pct,
    health_score,
    monthly_recurring_revenue,
    contract_renewal_date,
    days_to_renewal,
    account_created_at,
    first_paid_at,
    CASE
        WHEN current_state = 'trial' THEN account_created_at
        WHEN current_state = 'new_paid' THEN first_paid_at
        ELSE last_qualifying_event_at
    END as state_since,
    CURRENT_TIMESTAMP as state_updated_at
FROM account_state_logic
