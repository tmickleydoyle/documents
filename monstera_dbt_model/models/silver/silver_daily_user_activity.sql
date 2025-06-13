{{
  config(
    materialized='table',
    description='Daily user activity summary for engagement analysis'
  )
}}

-- Silver layer: Daily user activity
-- Aggregated daily activity per user for retention and engagement analysis

WITH daily_activity AS (
  SELECT
    entity_id as user_id,
    event_date,
    country,
    account_id,
    account_type,
    industry,
    user_tenure_days,

    -- Activity metrics
    COUNT(*) as total_events,
    COUNT(DISTINCT event_type) as unique_event_types,
    COUNT(DISTINCT session_id) as sessions_count,

    -- Event type breakdowns
    SUM(CASE WHEN event_type = 'user_login' THEN 1 ELSE 0 END) as logins,
    SUM(CASE WHEN event_type = 'video_create' THEN 1 ELSE 0 END) as videos_created,
    SUM(CASE WHEN event_type = 'video_upload' THEN 1 ELSE 0 END) as videos_uploaded,
    SUM(CASE WHEN event_type = 'project_create' THEN 1 ELSE 0 END) as projects_created,
    SUM(CASE WHEN event_type = 'comment_add' THEN 1 ELSE 0 END) as comments_added,

    -- Location breakdown
    COUNT(DISTINCT location) as locations_used,
    SUM(CASE WHEN location = 'web_app' THEN 1 ELSE 0 END) as web_events,
    SUM(CASE WHEN location = 'mobile_app' THEN 1 ELSE 0 END) as mobile_events,

    -- Time-based metrics
    MIN(event_timestamp) as first_event_time,
    MAX(event_timestamp) as last_event_time

  FROM {{ ref('silver_events_enriched') }}
  WHERE entity_type = 'user'
  GROUP BY 1,2,3,4,5,6,7
)

SELECT
  user_id,
  event_date,
  country,
  account_id,
  account_type,
  industry,
  user_tenure_days,

  -- Categorize user tenure for segmentation
  CASE
    WHEN user_tenure_days <= 7 THEN 'new_user'
    WHEN user_tenure_days <= 30 THEN 'recent_user'
    WHEN user_tenure_days <= 90 THEN 'established_user'
    ELSE 'veteran_user'
  END as user_tenure_segment,

  total_events,
  unique_event_types,
  sessions_count,
  logins,
  videos_created,
  videos_uploaded,
  projects_created,
  comments_added,
  locations_used,
  web_events,
  mobile_events,
  first_event_time,
  last_event_time,

  -- Engagement score (simple calculation)
  (videos_created * 3 + videos_uploaded * 2 + projects_created * 5 + comments_added * 1) as engagement_score

FROM daily_activity
