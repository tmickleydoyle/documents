{{
  config(
    materialized='table',
    description='Raw account entity data'
  )
}}

-- Bronze layer: Raw account data
-- Secondary entities that users belong to

SELECT
    account_id,
    account_name,
    account_type,
    industry,
    created_at,
    is_active
FROM {{ source('bronze', 'accounts') }}
WHERE account_id IS NOT NULL
