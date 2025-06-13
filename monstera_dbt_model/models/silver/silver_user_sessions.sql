{{
  config(
    materialized='table',
    description='User sessions derived from login/logout events'
  )
}}

-- Silver layer: User sessions
-- Derived from login/logout events to calculate engagement metrics

WITH login_logout_events AS (
  SELECT
    entity_id,
    event_type,
    event_timestamp,
    session_id,
    location,
    device_type,
    session_duration_minutes
  FROM {{ ref('silver_events_enriched') }}
  WHERE event_type IN ('user_login', 'user_logout')
),

sessions AS (
  SELECT
    login.session_id,
    login.entity_id as user_id,
    login.event_timestamp as session_start,
    logout.event_timestamp as session_end,
    login.location,
    login.device_type,
    CASE
      WHEN logout.event_timestamp IS NOT NULL
      THEN EXTRACT(epoch FROM logout.event_timestamp - login.event_timestamp) / 60.0
      ELSE logout.session_duration_minutes
    END as session_duration_minutes
  FROM login_logout_events login
  LEFT JOIN login_logout_events logout
    ON login.session_id = logout.session_id
    AND logout.event_type = 'user_logout'
  WHERE login.event_type = 'user_login'
)

SELECT
  session_id,
  user_id,
  session_start,
  session_end,
  location,
  device_type,
  session_duration_minutes,
  DATE(session_start) as session_date,
  EXTRACT(hour FROM session_start) as session_hour
FROM sessions
WHERE session_duration_minutes > 0
