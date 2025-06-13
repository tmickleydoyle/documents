-- Test that event schema compliance is above 95% (Monstera requirement)
-- This implements the data quality standard from the design doc

WITH schema_check AS (
  {{ validate_monstera_event_schema('bronze.events') }}
)

SELECT *
FROM schema_check
WHERE schema_compliance_rate < 95
