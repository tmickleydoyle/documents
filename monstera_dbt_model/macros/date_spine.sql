-- Macro to generate date spine when dbt_utils is not available
-- This is a fallback for the date_spine functionality

{% macro date_spine(datepart, start_date, end_date) %}

  {% set days_diff_query %}
    SELECT ({{ end_date }} - {{ start_date }})::int as days_diff
  {% endset %}

  {% if execute %}
    {% set results = run_query(days_diff_query) %}
    {% set days_diff = results.columns[0].values()[0] %}
  {% else %}
    {% set days_diff = 1000 %}
  {% endif %}

  WITH date_spine AS (
    SELECT
      {{ start_date }}::date + generate_series(0, {{ days_diff }}) as date_day
  )

  SELECT date_day FROM date_spine

{% endmacro %}
