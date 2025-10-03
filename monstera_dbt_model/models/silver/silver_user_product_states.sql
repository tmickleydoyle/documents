{{
  config(
    materialized='table',
    description='Product-specific user lifecycle states based on Monstera framework'
  )
}}

-- Silver layer: User Product States
-- Calculates product-specific lifecycle states for each user-product combination
--
-- Product-Specific States (from Monstera framework):
-- - never_adopted: User has platform account but never accessed this product
-- - new_to_product: First access within last 30 days, not yet activated
-- - active_in_product: Performed qualifying events within last 30 days
-- - dormant_in_product: No qualifying events for 31-60 days
-- - churned_from_product: No qualifying events for 61+ days
-- - reactivated_in_product: Returned after churn

WITH products AS (
    SELECT DISTINCT product_id
    FROM {{ ref('bronze_product_catalog') }}
    WHERE tier = 'product'
        AND is_active = true
),

users AS (
    SELECT DISTINCT user_id
    FROM {{ ref('bronze_users') }}
),

user_product_cartesian AS (
    SELECT
        u.user_id,
        p.product_id
    FROM users u
    CROSS JOIN products p
),

product_events AS (
    SELECT
        entity_id as user_id,
        product_id,
        MIN(event_timestamp) as first_access_at,
        MAX(CASE WHEN is_qualifying_event THEN event_timestamp END) as last_qualifying_event_at,
        MAX(CASE WHEN is_activation_event THEN event_timestamp END) as activation_date,
        COUNT(DISTINCT CASE WHEN is_qualifying_event THEN event_id END) as total_qualifying_events
    FROM {{ ref('bronze_events') }}
    WHERE entity_type = 'user'
        AND product_id IS NOT NULL
    GROUP BY 1, 2
),

product_state_logic AS (
    SELECT
        upc.user_id,
        upc.product_id,
        pe.first_access_at,
        pe.last_qualifying_event_at,
        pe.activation_date,
        COALESCE(pe.total_qualifying_events, 0) as total_qualifying_events,

        -- Calculate days since various events
        COALESCE(DATEDIFF('day', pe.first_access_at, CURRENT_DATE), 999) as days_since_first_access,
        COALESCE(DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE), 999) as days_since_last_qualifying_event,

        -- Determine product-specific state
        CASE
            -- Never adopted: No first access recorded
            WHEN pe.first_access_at IS NULL THEN 'never_adopted'

            -- New to product: First access within 30 days, not yet activated
            WHEN DATEDIFF('day', pe.first_access_at, CURRENT_DATE) <= 30
                AND pe.activation_date IS NULL
            THEN 'new_to_product'

            -- Active in product: Qualifying events within last 30 days
            WHEN pe.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE) <= 30
            THEN 'active_in_product'

            -- Dormant in product: No qualifying events for 31-60 days
            WHEN pe.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE) BETWEEN 31 AND 60
            THEN 'dormant_in_product'

            -- Churned from product: No qualifying events for 61+ days
            WHEN pe.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE) >= 61
            THEN 'churned_from_product'

            -- Churned: Accessed but never activated and past 30 days
            WHEN DATEDIFF('day', pe.first_access_at, CURRENT_DATE) > 30
                AND pe.activation_date IS NULL
            THEN 'churned_from_product'

            ELSE 'unknown'
        END as current_state,

        -- Determine when state began
        CASE
            WHEN pe.first_access_at IS NULL THEN NULL

            WHEN DATEDIFF('day', pe.first_access_at, CURRENT_DATE) <= 30
                AND pe.activation_date IS NULL
            THEN pe.first_access_at

            WHEN pe.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE) <= 30
            THEN pe.last_qualifying_event_at

            WHEN pe.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE) BETWEEN 31 AND 60
            THEN pe.last_qualifying_event_at + INTERVAL '31 days'

            WHEN pe.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', pe.last_qualifying_event_at, CURRENT_DATE) >= 61
            THEN pe.last_qualifying_event_at + INTERVAL '61 days'

            ELSE pe.first_access_at
        END as state_since

    FROM user_product_cartesian upc
    LEFT JOIN product_events pe ON upc.user_id = pe.user_id AND upc.product_id = pe.product_id
)

SELECT
    user_id,
    product_id,
    current_state,
    state_since,
    first_access_at,
    last_qualifying_event_at,
    activation_date,
    total_qualifying_events,
    days_since_first_access,
    days_since_last_qualifying_event,
    CURRENT_TIMESTAMP as state_updated_at
FROM product_state_logic
