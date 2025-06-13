{{
  config(
    materialized='table',
    description='Raw user entity data'
  )
}}

-- Bronze layer: Raw user data
-- Primary entities that perform actions in the system

SELECT
    user_id,
    email,
    first_name,
    last_name,
    country,
    account_id,
    created_at,
    is_active
FROM {{ source('bronze', 'users') }}
WHERE user_id IS NOT NULL
