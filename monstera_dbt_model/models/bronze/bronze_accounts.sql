{{
  config(
    materialized='table',
    description='Account entity data for B2B lifecycle tracking'
  )
}}

-- Bronze layer: Account entity data
-- Accounts represent teams, organizations, or companies using the platform
-- Track account-level lifecycle states and subscription information
--
-- Key fields for Account Lifecycle States (from Monstera framework):
-- - subscription_tier: Plan level (trial, starter, professional, enterprise)
-- - total_seats: Number of licensed seats
-- - account_created_at: Account creation timestamp
-- - first_paid_at: When account first converted to paid
-- - contract_renewal_date: Next renewal date for subscription
-- - monthly_recurring_revenue: Current MRR from this account
-- - is_trial: Whether account is in trial period

SELECT
    account_id,
    account_name,
    subscription_tier,
    total_seats,
    account_created_at,
    first_paid_at,
    contract_renewal_date,
    monthly_recurring_revenue,
    is_trial
FROM {{ ref('seed_accounts') }}
WHERE account_id IS NOT NULL
