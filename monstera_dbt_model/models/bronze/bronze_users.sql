{{
  config(
    materialized='table',
    description='User entity data for lifecycle state tracking'
  )
}}

-- Bronze layer: User entity data
-- Primary entities that perform actions in the system
-- Users are the primary entity type for user lifecycle states
--
-- Key fields for User Lifecycle States (from Monstera framework):
-- - user_id: Unique identifier
-- - email: Contact information
-- - account_id: Associated account/team
-- - user_created_at: Signup timestamp (for New user time window)
-- - country: Geographic segmentation
-- - plan_type: User's subscription plan (for segmentation)
-- - acquisition_source: How user was acquired (for cohort analysis)

SELECT
    user_id,
    email,
    account_id,
    user_created_at,
    country,
    plan_type,
    acquisition_source
FROM {{ ref('seed_users') }}
WHERE user_id IS NOT NULL
