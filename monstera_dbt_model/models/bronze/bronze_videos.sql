{{
  config(
    materialized='table',
    description='Raw video entity data'
  )
}}

-- Bronze layer: Raw video data
-- Secondary entities created by users within projects

SELECT
    video_id,
    video_title,
    project_id,
    created_by_user_id,
    duration_seconds,
    status,
    created_at,
    published_at
FROM {{ source('bronze', 'videos') }}
WHERE video_id IS NOT NULL
