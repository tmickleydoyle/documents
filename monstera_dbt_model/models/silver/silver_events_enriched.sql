{{
  config(
    materialized='table',
    description='Cleaned and enriched events with entity information - Silver layer following Monstera framework'
  )
}}

-- Silver layer: Events enriched with entity data
-- This model joins action data with entity data as described in the Monstera implementation guide
-- "Enriching action data with entity data" enables segmented metrics

WITH enriched_events AS (
  SELECT
    e.event_id,
    e.entity_id,
    e.entity_type,
    e.event_type,
    e.event_timestamp,
    e.location,
    e.session_id,
    e.metadata,

    -- Enrich with user data
    u.email,
    u.first_name,
    u.last_name,
    u.country,
    u.account_id,
    u.created_at as user_created_at,

    -- Enrich with account data
    a.account_name,
    a.account_type,
    a.industry,
    a.created_at as account_created_at,

    -- Calculate user tenure at time of event (for segmentation)
    DATE_PART('days', e.event_timestamp - u.created_at) as user_tenure_days,

    -- Extract metadata fields for common analysis
    (e.metadata->>'project_id')::TEXT as project_id,
    (e.metadata->>'video_id')::TEXT as video_id,
    (e.metadata->>'device_type')::TEXT as device_type,
    (e.metadata->>'session_duration_minutes')::INTEGER as session_duration_minutes,

    -- Date dimensions for time-based analysis
    DATE(e.event_timestamp) as event_date,
    DATE_TRUNC('week', e.event_timestamp) as event_week,
    DATE_TRUNC('month', e.event_timestamp) as event_month,
    DATE_TRUNC('quarter', e.event_timestamp) as event_quarter,
    EXTRACT(hour FROM e.event_timestamp) as event_hour,
    EXTRACT(dow FROM e.event_timestamp) as day_of_week

  FROM {{ ref('bronze_events') }} e
  LEFT JOIN {{ ref('bronze_users') }} u ON e.entity_id = u.user_id
  LEFT JOIN {{ ref('bronze_accounts') }} a ON u.account_id = a.account_id
)

SELECT * FROM enriched_events
