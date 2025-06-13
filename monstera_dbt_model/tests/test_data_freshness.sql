-- Test for data freshness - events should be recent
-- Implements <2 hour data freshness requirement

SELECT
  'events_freshness_check' as test_name,
  MAX(created_at) as latest_event,
  EXTRACT(epoch FROM (CURRENT_TIMESTAMP - MAX(created_at))) / 3600 as hours_since_latest
FROM bronze.events
HAVING EXTRACT(epoch FROM (CURRENT_TIMESTAMP - MAX(created_at))) / 3600 > 2
