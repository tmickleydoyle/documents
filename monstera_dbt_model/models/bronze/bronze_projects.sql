{{
  config(
    materialized='table',
    description='Raw project entity data'
  )
}}

-- Bronze layer: Raw project data
-- Secondary entities created by users

SELECT
    project_id,
    project_name,
    account_id,
    created_by_user_id,
    status,
    created_at,
    updated_at
FROM {{ source('bronze', 'projects') }}
WHERE project_id IS NOT NULL
