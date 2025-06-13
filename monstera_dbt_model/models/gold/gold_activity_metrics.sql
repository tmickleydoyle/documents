{{
  config(
    materialized='table',
    description='Activity View metrics - Granular event-level insights (Monstera Framework Dashboard Type 3)'
  )
}}

-- Gold layer: Activity View Dashboard
-- Most granular level focusing on specific actions and workflows
-- Detailed user behavior and event patterns as described in Monstera design

WITH daily_activity_patterns AS (
  SELECT
    DATE(event_timestamp) as event_date,
    event_type,
    location,
    EXTRACT(hour FROM event_timestamp) as event_hour,
    EXTRACT(dow FROM event_timestamp) as day_of_week,
    country,
    COALESCE(metadata->>'device_type', 'unknown') as device_type,

    -- Event volume metrics
    COUNT(*) as event_count,
    COUNT(DISTINCT entity_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,

    -- Event-specific metrics based on metadata
    COUNT(CASE WHEN metadata->>'project_id' IS NOT NULL THEN 1 END) as events_with_project,
    COUNT(CASE WHEN metadata->>'video_id' IS NOT NULL THEN 1 END) as events_with_video

  FROM {{ ref('silver_events_enriched') }}
  WHERE DATE(event_timestamp) >= CURRENT_DATE - INTERVAL '18 months'
    AND entity_type = 'user'
  GROUP BY 1,2,3,4,5,6,7
),

event_funnels AS (
  SELECT
    DATE(event_timestamp) as event_date,
    entity_id as user_id,
    session_id,

    -- Video creation workflow funnel
    MAX(CASE WHEN event_type = 'video_create' THEN 1 ELSE 0 END) as created_video,
    MAX(CASE WHEN event_type = 'video_upload' THEN 1 ELSE 0 END) as uploaded_video,
    MAX(CASE WHEN event_type = 'video_publish' THEN 1 ELSE 0 END) as published_video,

    -- Project workflow funnel
    MAX(CASE WHEN event_type = 'project_create' THEN 1 ELSE 0 END) as created_project,
    MAX(CASE WHEN event_type = 'project_update' THEN 1 ELSE 0 END) as updated_project,

    -- Session engagement
    MAX(CASE WHEN event_type = 'comment_add' THEN 1 ELSE 0 END) as added_comment,
    COUNT(DISTINCT event_type) as unique_actions_in_session

  FROM {{ ref('silver_events_enriched') }}
  WHERE DATE(event_timestamp) >= CURRENT_DATE - INTERVAL '18 months'
    AND entity_type = 'user'
    AND session_id IS NOT NULL
  GROUP BY 1,2,3
),

funnel_summary AS (
  SELECT
    event_date,

    -- Video creation funnel metrics
    COUNT(DISTINCT CASE WHEN created_video = 1 THEN user_id END) as users_created_video,
    COUNT(DISTINCT CASE WHEN uploaded_video = 1 THEN user_id END) as users_uploaded_video,
    COUNT(DISTINCT CASE WHEN published_video = 1 THEN user_id END) as users_published_video,

    -- Conversion rates in video workflow
    ROUND(COUNT(DISTINCT CASE WHEN uploaded_video = 1 THEN user_id END) * 100.0 /
          NULLIF(COUNT(DISTINCT CASE WHEN created_video = 1 THEN user_id END), 0), 2) as create_to_upload_rate,

    ROUND(COUNT(DISTINCT CASE WHEN published_video = 1 THEN user_id END) * 100.0 /
          NULLIF(COUNT(DISTINCT CASE WHEN uploaded_video = 1 THEN user_id END), 0), 2) as upload_to_publish_rate,

    -- Project workflow metrics
    COUNT(DISTINCT CASE WHEN created_project = 1 THEN user_id END) as users_created_project,
    COUNT(DISTINCT CASE WHEN updated_project = 1 THEN user_id END) as users_updated_project,

    -- Session depth metrics
    AVG(unique_actions_in_session) as avg_actions_per_session,
    COUNT(DISTINCT CASE WHEN unique_actions_in_session >= 3 THEN session_id END) as deep_engagement_sessions,
    COUNT(DISTINCT session_id) as total_sessions

  FROM event_funnels
  GROUP BY event_date
)

-- Final activity metrics combining patterns and funnels
SELECT
  dap.event_date,
  dap.event_type,
    dap.location,
  dap.event_count,
  dap.unique_users,
  dap.unique_sessions,

  -- Time patterns
  dap.event_hour,
  dap.day_of_week,

  -- Platform and geography
  dap.country,
  dap.device_type,

  -- Event context
  dap.events_with_project,
  dap.events_with_video,

  -- Funnel metrics (when available)
  fs.users_created_video,
  fs.users_uploaded_video,
  fs.users_published_video,
  fs.create_to_upload_rate,
  fs.upload_to_publish_rate,
  fs.avg_actions_per_session,
  fs.deep_engagement_sessions,

  -- Activity intensity scoring
  CASE
    WHEN dap.event_count >= 100 THEN 'high'
    WHEN dap.event_count >= 20 THEN 'medium'
    ELSE 'low'
  END as activity_intensity,

  -- User engagement level based on activity volume
  CASE
    WHEN dap.unique_users >= 10 THEN 'highly_active'
    WHEN dap.unique_users >= 5 THEN 'moderately_active'
    ELSE 'low_activity'
  END as user_engagement_segment

FROM daily_activity_patterns dap
LEFT JOIN funnel_summary fs ON dap.event_date = fs.event_date
WHERE dap.event_date IS NOT NULL
ORDER BY dap.event_date DESC, dap.event_count DESC
