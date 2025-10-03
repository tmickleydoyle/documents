{{
  config(
    materialized='table',
    description='Product catalog for product taxonomy and hierarchy'
  )
}}

-- Bronze layer: Product Catalog
-- Defines the product taxonomy and hierarchy for the Monstera framework
--
-- Product Hierarchy (from Monstera framework):
-- Tier 1: Product Family - highest level grouping (content_creation, collaboration, analytics)
-- Tier 2: Product - individual products within a family
-- Tier 3: Feature - specific capabilities within a product
-- Tier 4: Sub-Feature - granular functionality within a feature
--
-- Key fields:
-- - product_id: Unique identifier (snake_case)
-- - product_name: Human-readable name (Title Case)
-- - product_family_id: Parent family identifier
-- - tier: Hierarchy level (family/product/feature)
-- - parent_product_id: Parent product if this is a feature
-- - is_active: Whether product is currently active
-- - created_at: When product was launched

SELECT
    product_id,
    product_name,
    product_family_id,
    tier,
    parent_product_id,
    is_active,
    created_at
FROM {{ ref('seed_product_catalog') }}
WHERE product_id IS NOT NULL
