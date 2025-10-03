{{
  config(
    materialized='table',
    description='Raw events data following Monstera standardized schema with product taxonomy'
  )
}}

-- Bronze layer: Raw events data as ingested from source systems
-- This model provides a clean interface to the raw events table
-- following the Monstera event schema standards
--
-- Schema Requirements (from Monstera framework):
-- - entity_id: Unique identifier for the entity performing the action
-- - entity_type: Classification of the entity (user, account, organization, etc.)
-- - event_type: Specific action taken (signup, login, create_video, etc.)
-- - timestamp: When the event occurred (ISO 8601)
-- - location: Where the event occurred (web app, mobile app, API, etc.)
-- - session_id: Session identifier (optional)
-- - product_id: Product where event occurred (required for product-level metrics)
-- - is_qualifying_event: Boolean indicating if event qualifies for user state calculations
-- - is_activation_event: Boolean indicating if event contributes to product activation
-- - metadata: Additional context specific to the event type (JSON)

SELECT
    event_id,
    entity_id,
    entity_type,
    event_type,
    timestamp as event_timestamp,
    location,
    session_id,
    product_id,
    COALESCE(is_qualifying_event, false) as is_qualifying_event,
    COALESCE(is_activation_event, false) as is_activation_event,
    metadata,
    timestamp as created_at
FROM {{ ref('seed_events') }}

-- Basic data quality filters (Monstera validation rules)
WHERE entity_id IS NOT NULL
  AND entity_type IS NOT NULL
  AND event_type IS NOT NULL
  AND timestamp IS NOT NULL
  AND location IS NOT NULL
  -- Timestamps must be realistic (not in future, not too far in past)
  AND timestamp <= CURRENT_TIMESTAMP
  AND timestamp >= '2020-01-01'
