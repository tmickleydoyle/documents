{{
  config(
    materialized='table',
    description='Current user lifecycle states based on Monstera framework'
  )
}}

-- Silver layer: User Current State
-- Calculates current lifecycle state for each user based on Monstera framework
--
-- User Lifecycle States (from Monstera framework):
-- - new: 0-30 days from signup, not yet reached Active threshold
-- - active: Performed qualifying events within last 30 days
-- - returning: Re-engaged after period of inactivity (transient state)
-- - dormant: No qualifying events for 31-60 days
-- - churned: No qualifying events for 61+ days
-- - reactivated: Returned after being churned (61+ days)
-- - deleted: Account deleted or banned
--
-- Time-Based State Definitions:
-- | State    | Minimum Activity        | Maximum Inactivity | Time Window                  |
-- |----------|------------------------|-------------------|-------------------------------|
-- | new      | Account creation       | N/A               | 0-30 days from signup         |
-- | active   | 1+ qualifying events   | 30 days           | Last 30 days                  |
-- | dormant  | 0 qualifying events    | 31-60 days        | 31-60 days since last activity|
-- | churned  | 0 qualifying events    | 61+ days          | 61+ days since last activity  |

WITH user_events AS (
    SELECT
        e.entity_id as user_id,
        u.user_created_at,
        MAX(CASE WHEN e.is_qualifying_event THEN e.event_timestamp END) as last_qualifying_event_at,
        MAX(e.event_timestamp) as last_any_event_at,
        COUNT(DISTINCT CASE WHEN e.is_qualifying_event THEN e.event_id END) as total_qualifying_events
    FROM {{ ref('bronze_events') }} e
    INNER JOIN {{ ref('bronze_users') }} u ON e.entity_id = u.user_id
    WHERE e.entity_type = 'user'
    GROUP BY 1, 2
),

user_state_logic AS (
    SELECT
        u.user_id,
        u.email,
        u.account_id,
        u.user_created_at,
        ue.last_qualifying_event_at,
        ue.last_any_event_at,
        ue.total_qualifying_events,

        -- Calculate days since various events
        DATEDIFF('day', u.user_created_at, CURRENT_DATE) as days_since_signup,
        COALESCE(DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE), 999) as days_since_last_qualifying_event,

        -- Determine platform-wide state based on activity
        CASE
            -- New: 0-30 days from signup and hasn't reached active threshold
            WHEN DATEDIFF('day', u.user_created_at, CURRENT_DATE) <= 30
                AND (ue.last_qualifying_event_at IS NULL OR ue.total_qualifying_events < 3)
            THEN 'new'

            -- Active: Has qualifying events within last 30 days
            WHEN ue.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE) <= 30
            THEN 'active'

            -- Dormant: No qualifying events for 31-60 days
            WHEN ue.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE) BETWEEN 31 AND 60
            THEN 'dormant'

            -- Churned: No qualifying events for 61+ days
            WHEN ue.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE) >= 61
            THEN 'churned'

            -- Churned: New user who never activated within 30 days
            WHEN DATEDIFF('day', u.user_created_at, CURRENT_DATE) > 30
                AND (ue.last_qualifying_event_at IS NULL OR ue.total_qualifying_events < 3)
            THEN 'churned'

            ELSE 'unknown'
        END as platform_state,

        -- Determine when state began
        CASE
            WHEN DATEDIFF('day', u.user_created_at, CURRENT_DATE) <= 30
                AND (ue.last_qualifying_event_at IS NULL OR ue.total_qualifying_events < 3)
            THEN u.user_created_at

            WHEN ue.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE) <= 30
            THEN ue.last_qualifying_event_at

            WHEN ue.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE) BETWEEN 31 AND 60
            THEN ue.last_qualifying_event_at + INTERVAL '31 days'

            WHEN ue.last_qualifying_event_at IS NOT NULL
                AND DATEDIFF('day', ue.last_qualifying_event_at, CURRENT_DATE) >= 61
            THEN ue.last_qualifying_event_at + INTERVAL '61 days'

            ELSE u.user_created_at
        END as platform_state_since

    FROM {{ ref('bronze_users') }} u
    LEFT JOIN user_events ue ON u.user_id = ue.user_id
)

SELECT
    user_id,
    email,
    account_id,
    user_created_at,
    platform_state,
    platform_state_since,
    last_qualifying_event_at,
    last_any_event_at,
    total_qualifying_events,
    days_since_signup,
    days_since_last_qualifying_event,
    CURRENT_TIMESTAMP as state_updated_at
FROM user_state_logic
