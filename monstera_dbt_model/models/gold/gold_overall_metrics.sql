{{
  config(
    materialized='table',
    description='Overall View metrics - Company-wide KPIs and trends (Monstera Framework Dashboard Type 1)'
  )
}}

-- Gold layer: Overall View Dashboard
-- Top-level dashboards for leadership and strategic decision-making
-- Includes big number tiles and trends over last 90 days as per Monstera design

WITH date_spine AS (
  {{ dbt_utils.date_spine(
      datepart="day",
      start_date="cast('2023-01-01' as date)",
      end_date="cast('2025-12-31' as date)"
  ) }}
),

daily_metrics AS (
  SELECT
    event_date,

    -- Activity Metrics: What entities are doing
    COUNT(DISTINCT user_id) as daily_active_users,
    SUM(total_events) as total_daily_events,
    SUM(logins) as total_daily_logins,
    SUM(videos_created) as total_videos_created,
    SUM(videos_uploaded) as total_videos_uploaded,
    SUM(projects_created) as total_projects_created,
    SUM(comments_added) as total_comments_added,

    -- Engagement Metrics: How entities are interacting
    AVG(engagement_score) as avg_engagement_score,
    AVG(sessions_count) as avg_sessions_per_user,
    COUNT(DISTINCT CASE WHEN total_events >= 5 THEN user_id END) as highly_active_users,

    -- Location usage
    SUM(web_events) as total_web_events,
    SUM(mobile_events) as total_mobile_events,

    -- New user acquisition
    COUNT(DISTINCT CASE WHEN user_tenure_segment = 'new_user' THEN user_id END) as new_users_active

  FROM {{ ref('silver_daily_user_activity') }}
  GROUP BY event_date
),

rolling_metrics AS (
  SELECT
    d.date_day as metric_date,

    -- Current day metrics
    COALESCE(dm.daily_active_users, 0) as daily_active_users,
    COALESCE(dm.total_daily_events, 0) as total_daily_events,
    COALESCE(dm.total_videos_created, 0) as total_videos_created,
    COALESCE(dm.avg_engagement_score, 0) as avg_engagement_score,

    -- 7-day rolling averages
    AVG(COALESCE(dm.daily_active_users, 0)) OVER (
      ORDER BY d.date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as dau_7day_avg,

    AVG(COALESCE(dm.total_daily_events, 0)) OVER (
      ORDER BY d.date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as events_7day_avg,

    -- 30-day rolling metrics
    SUM(COALESCE(dm.daily_active_users, 0)) OVER (
      ORDER BY d.date_day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as mau_30day,

    SUM(COALESCE(dm.total_videos_created, 0)) OVER (
      ORDER BY d.date_day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as videos_created_30day,

    -- Growth metrics (compared to previous periods)
    LAG(COALESCE(dm.daily_active_users, 0), 7) OVER (ORDER BY d.date_day) as dau_prev_week,
    LAG(COALESCE(dm.daily_active_users, 0), 30) OVER (ORDER BY d.date_day) as dau_prev_month

  FROM date_spine d
  LEFT JOIN daily_metrics dm ON d.date_day = dm.event_date
  WHERE d.date_day >= '2023-01-01'
)

SELECT
  metric_date,
  daily_active_users,
  total_daily_events,
  total_videos_created,
  avg_engagement_score,
  dau_7day_avg,
  events_7day_avg,
  mau_30day,
  videos_created_30day,

  -- Growth calculations
  CASE
    WHEN dau_prev_week > 0
    THEN ROUND(((daily_active_users - dau_prev_week) * 100.0 / dau_prev_week), 2)
    ELSE NULL
  END as dau_wow_growth_pct,

  CASE
    WHEN dau_prev_month > 0
    THEN ROUND(((daily_active_users - dau_prev_month) * 100.0 / dau_prev_month), 2)
    ELSE NULL
  END as dau_mom_growth_pct,

  -- Current period indicators (for big number tiles)
  metric_date = CURRENT_DATE - 1 as is_current_day,
  metric_date >= CURRENT_DATE - 90 as is_last_90_days

FROM rolling_metrics
ORDER BY metric_date DESC
