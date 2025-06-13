{{
  config(
    materialized='table',
    description='Segment View metrics - Metrics broken down by entity characteristics (Monstera Framework Dashboard Type 2)'
  )
}}

-- Gold layer: Segment View Dashboard
-- Focus on breaking down overall metrics by key entity segments
-- Geography, account type, user tenure as described in Monstera design
-- Up to 18 months of data for line and bar charts

WITH monthly_segments AS (
  SELECT
    DATE_TRUNC('month', event_date) as event_month,

    -- Segmentation dimensions
    country,
    account_type,
    industry,
    user_tenure_segment,

    -- Aggregated metrics by segment
    COUNT(DISTINCT user_id) as monthly_active_users,
    SUM(total_events) as total_events,
    SUM(videos_created) as videos_created,
    SUM(videos_uploaded) as videos_uploaded,
    SUM(projects_created) as projects_created,
    AVG(engagement_score) as avg_engagement_score,

    -- Platform usage
    SUM(web_events) as web_events,
    SUM(mobile_events) as mobile_events,
    ROUND(SUM(mobile_events) * 100.0 / NULLIF(SUM(web_events + mobile_events), 0), 2) as mobile_usage_pct,

    -- User behavior patterns
    AVG(sessions_count) as avg_sessions_per_user,
    COUNT(DISTINCT CASE WHEN engagement_score >= 10 THEN user_id END) as highly_engaged_users

  FROM {{ ref('silver_daily_user_activity') }}
  WHERE event_date >= CURRENT_DATE - INTERVAL '18 months'
  GROUP BY 1,2,3,4,5
),

segment_growth AS (
  SELECT
    *,

    -- Month-over-month growth by segment
    LAG(monthly_active_users) OVER (
      PARTITION BY country, account_type, industry, user_tenure_segment
      ORDER BY event_month
    ) as prev_month_mau,

    -- Calculate growth rates
    CASE
      WHEN LAG(monthly_active_users) OVER (
        PARTITION BY country, account_type, industry, user_tenure_segment
        ORDER BY event_month
      ) > 0
      THEN ROUND((
        (monthly_active_users - LAG(monthly_active_users) OVER (
          PARTITION BY country, account_type, industry, user_tenure_segment
          ORDER BY event_month
        )) * 100.0 / LAG(monthly_active_users) OVER (
          PARTITION BY country, account_type, industry, user_tenure_segment
          ORDER BY event_month
        )
      ), 2)
      ELSE NULL
    END as mau_growth_pct

  FROM monthly_segments
)

SELECT
  event_month,
  country,
  account_type,
  industry,
  user_tenure_segment,
  monthly_active_users,
  total_events,
  videos_created,
  videos_uploaded,
  projects_created,
  avg_engagement_score,
  web_events,
  mobile_events,
  mobile_usage_pct,
  avg_sessions_per_user,
  highly_engaged_users,
  mau_growth_pct,

  -- Ranking within segments for identifying top performers
  ROW_NUMBER() OVER (
    PARTITION BY event_month
    ORDER BY monthly_active_users DESC
  ) as country_rank_by_mau,

  ROW_NUMBER() OVER (
    PARTITION BY event_month, country
    ORDER BY monthly_active_users DESC
  ) as account_type_rank_by_mau,

  -- Share of total activity by segment
  ROUND(monthly_active_users * 100.0 / SUM(monthly_active_users) OVER (
    PARTITION BY event_month
  ), 2) as mau_share_pct

FROM segment_growth
WHERE event_month IS NOT NULL
ORDER BY event_month DESC, monthly_active_users DESC
