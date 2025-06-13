{{
  config(
    materialized='table',
    description='Raw events data following Monstera standardized schema'
  )
}}

-- Bronze layer: Raw events data as ingested from source systems
-- This model provides a clean interface to the raw events table
-- following the Monstera event schema standards

SELECT
    event_id,
    entity_id,
    entity_type,
    event_type,
    timestamp as event_timestamp,
    location,
    session_id,
    metadata,
    created_at
FROM {{ source('bronze', 'events') }}

-- Basic data quality filters
WHERE entity_id IS NOT NULL
  AND entity_type IS NOT NULL
  AND event_type IS NOT NULL
  AND timestamp IS NOT NULL
  AND location IS NOT NULL
