-- Macro for Monstera event validation
-- Ensures events follow the standardized schema

{% macro validate_monstera_event_schema(table_name) %}

  SELECT
    '{{ table_name }}' as table_name,
    COUNT(*) as total_events,
    COUNT(CASE WHEN entity_id IS NULL THEN 1 END) as missing_entity_id,
    COUNT(CASE WHEN entity_type IS NULL THEN 1 END) as missing_entity_type,
    COUNT(CASE WHEN event_type IS NULL THEN 1 END) as missing_event_type,
    COUNT(CASE WHEN timestamp IS NULL THEN 1 END) as missing_timestamp,
    COUNT(CASE WHEN location IS NULL THEN 1 END) as missing_location,

    -- Schema compliance rate
    ROUND((COUNT(*) - COUNT(CASE WHEN entity_id IS NULL OR entity_type IS NULL OR
                                  event_type IS NULL OR timestamp IS NULL OR
                                  location IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as schema_compliance_rate

  FROM {{ table_name }}

{% endmacro %}
