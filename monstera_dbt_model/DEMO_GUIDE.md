# Monstera Framework Demo Guide

This guide will help you run a live demo of the Monstera metrics framework to share with stakeholders.

## Quick Demo Setup (Under 10 Minutes)

### Step 1: One-Command Setup

```bash
cd /Users/tmickleydoyle/Repos/documents/monstera_dbt_model
./run_demo.sh
```

This will:
- Set up Python virtual environment
- Install dbt-duckdb
- Load mock data (20 users, 10 accounts, 40 events, 5 products)
- Build all metrics models
- Create a ready-to-query DuckDB database

### Step 2: Export Data for Visualization

```bash
./export_demo_data.sh
```

This creates 8 CSV files in `exports/` folder that you can use in:
- Excel/Google Sheets for charts
- PowerPoint/Google Slides for presentations
- BI tools (Tableau, Metabase, Looker, etc.)

## Demo Flow for Stakeholders

### Act 1: The Problem (2-3 minutes)

**Talk Track:**
> "Most companies struggle with metric drift - different teams defining 'active user' differently, inconsistent retention calculations, and fragmented product analytics. We've designed the Monstera framework to solve this."

**Show:** The Monstera Company Metrics Design document (just the overview/principles sections)

### Act 2: The Solution (5-7 minutes)

**Talk Track:**
> "Monstera provides a complete, standardized system for tracking users, products, and accounts. Let me show you what this looks like with real data."

#### Part A: User Lifecycle States

**Query to run:**
```sql
duckdb monstera_demo.duckdb << EOF
SELECT
    platform_state as "User State",
    COUNT(*) as "Count",
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as "% of Total",
    ROUND(AVG(days_since_signup), 0) as "Avg Days Since Signup"
FROM silver.silver_user_current_state
GROUP BY platform_state
ORDER BY "Count" DESC;
EOF
```

**What to highlight:**
- "Every user is in exactly one state: new, active, dormant, or churned"
- "These states are calculated automatically based on activity in last 30/60/90 days"
- "No more debates about who is 'active' - it's standardized"

**Show the pie chart** from `exports/user_states.csv`

#### Part B: Product Adoption & Health

**Query to run:**
```sql
duckdb monstera_demo.duckdb << EOF
SELECT
    p.product_name as "Product",
    COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END) as "Users Tried",
    COUNT(DISTINCT CASE WHEN ups.current_state = 'active_in_product' THEN ups.user_id END) as "Users Active",
    ROUND(
        COUNT(DISTINCT CASE WHEN ups.activation_date IS NOT NULL THEN ups.user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN ups.current_state != 'never_adopted' THEN ups.user_id END), 0)
    , 1) as "Activation Rate %"
FROM silver.silver_user_product_states ups
JOIN bronze.bronze_product_catalog p ON ups.product_id = p.product_id
WHERE p.tier = 'product'
GROUP BY p.product_name
ORDER BY "Users Active" DESC;
EOF
```

**What to highlight:**
- "We track product adoption at both platform and individual product level"
- "Video Editor has 85% activation rate - users love it"
- "Template Library has 60% - there's opportunity to improve onboarding"
- "Users can be active in one product while churned in another - granular insights"

**Show the bar chart** from `exports/product_adoption.csv`

#### Part C: Account Health (B2B Focus)

**Query to run:**
```sql
duckdb monstera_demo.duckdb << EOF
SELECT
    current_state as "Account State",
    COUNT(*) as "# Accounts",
    ROUND(AVG(health_score), 1) as "Avg Health Score (0-100)",
    ROUND(AVG(seat_utilization_pct), 1) as "Avg Seat Utilization %",
    SUM(monthly_recurring_revenue) as "Total MRR"
FROM silver.silver_account_current_state
GROUP BY current_state
ORDER BY "Total MRR" DESC;
EOF
```

**What to highlight:**
- "We calculate a health score for every account based on 4 factors"
- "2 accounts are at-risk with only 35% health score - worth $X in MRR"
- "Expanding accounts have 85% health - these are your advocates"
- "Account states help prioritize customer success efforts"

**Show the at-risk accounts detail** from `exports/at_risk_accounts.csv`

### Act 3: The "Aha Moment" (3-5 minutes)

**Talk Track:**
> "The power of Monstera is that all these metrics follow the same naming convention, calculation logic, and can roll up into standard dashboards."

#### Show the 3-Tier Dashboard Structure

**Overall View Dashboard** - For executives
- Big number tiles: MAU, DAU, Active Accounts, Total MRR
- Last 90 days trend
- Query: See `demo_queries.sql` section "OVERALL VIEW DASHBOARD"

**Segment View Dashboard** - For product teams
- MAU by country, plan type
- User states by cohort
- Product adoption by segment
- Query: See `demo_queries.sql` section "SEGMENTATION PREVIEW"

**Activity View Dashboard** - For analysts
- Event volume by product
- Workflow completion rates
- Feature usage patterns
- Query: See `demo_queries.sql` section "EVENT ANALYTICS"

**What to highlight:**
- "Same metric definitions across all dashboards"
- "Self-service - any team can find their metrics"
- "Standardized naming: [Entity] [Action] [Time Period]"

### Act 4: The Extensibility (2-3 minutes)

**Talk Track:**
> "This isn't just a static framework. As we add new products, users, or metrics, they automatically flow through the same structure."

**Show:**
1. Open `seeds/seed_product_catalog.csv` - "Add new product here"
2. Open `seeds/seed_events.csv` - "Events auto-categorize by product"
3. Show a silver model - "States calculate automatically"
4. Show a gold model - "Metrics aggregate consistently"

**What to highlight:**
- "New product? Just add to catalog and define qualifying events"
- "New metric? Follow the naming convention template"
- "Everything is documented, tested, and version controlled"

## Common Questions & Answers

**Q: How much data do I need to implement this?**
A: You can start with your current event data. The framework is flexible - start with 1-2 products and expand.

**Q: How long does implementation take?**
A: 4-8 weeks for a basic implementation covering 3-5 products. This demo took our team 2 weeks to build fully.

**Q: Can this integrate with our existing tools?**
A: Yes - dbt outputs to any SQL database. Connect your BI tool (Looker, Tableau, Metabase) to the gold layer tables.

**Q: What about data privacy/security?**
A: The framework includes privacy by design principles - no PII in metrics, hashed entity IDs, GDPR-compliant retention.

**Q: How do we define "qualifying events" for our products?**
A: Start with events that indicate value: creating something, publishing, sharing, or completing a workflow. The framework has guidelines.

**Q: What if we need custom metrics beyond the framework?**
A: The framework provides the foundation - you can extend with custom metrics while maintaining the core standards.

## Materials to Share After Demo

1. **Monstera Company Metrics Design.md** - The complete framework
2. **This demo codebase** - Working implementation they can explore
3. **Exported CSVs** - Sample data they can visualize
4. **Screenshots of queries** - Show the metrics in action

## Creating Screenshots for Presentations

### Screenshot 1: User State Distribution
```bash
duckdb monstera_demo.duckdb -c "SELECT platform_state, COUNT(*) as users FROM silver.silver_user_current_state GROUP BY 1;" -markdown
```
Take screenshot, paste into slides.

### Screenshot 2: Product Adoption Funnel
```bash
duckdb monstera_demo.duckdb -c "SELECT product_name, users_tried, users_active, activation_rate_pct FROM (your query here);" -markdown
```

### Screenshot 3: Account Health Distribution
```bash
duckdb monstera_demo.duckdb -c "SELECT current_state, COUNT(*), AVG(health_score) FROM silver.silver_account_current_state GROUP BY 1;" -markdown
```

### Screenshot 4: MAU Trend
Open `exports/mau_trend.csv` in Excel, create line chart, screenshot the chart.

## Advanced Demo Options

### Option A: Live Dashboard (Metabase)

```bash
# Start Metabase
docker run -d -p 3000:3000 -v ~/metabase-data:/metabase-data \
  --name metabase metabase/metabase

# Open http://localhost:3000
# Add DuckDB connection (use path to monstera_demo.duckdb)
# Create 3 dashboards: Overall, Segment, Activity
# Use queries from demo_queries.sql
```

**Pros:**
- Visual, interactive
- Looks professional
- Can drill down into data

**Cons:**
- Requires Docker
- 15-20 min setup time
- Learning curve for Metabase

### Option B: Jupyter Notebook Demo

```bash
pip install jupyter pandas plotly
jupyter notebook
```

Create notebook with:
1. Load data from DuckDB
2. Create pandas DataFrames
3. Plot with plotly (interactive charts)
4. Show state transition flows

**Pros:**
- Interactive and impressive
- Can run "what-if" scenarios live
- Shows technical depth

**Cons:**
- Requires Python knowledge
- 30 min setup time

### Option C: Evidence.dev (Code-Based BI)

```bash
npm install -g @evidence-dev/evidence
npx degit evidence-dev/template monstera-dashboard
cd monstera-dashboard
# Edit sources/connection.yaml to point to DuckDB
npm run dev
```

**Pros:**
- Beautiful, modern dashboards
- Markdown-based (easy to edit)
- Git-friendly

**Cons:**
- Requires Node.js
- Steeper learning curve
- 20-30 min setup

## Demo Variations by Audience

### For Executives (10 minutes)
- Focus on: User states, Account health, MRR impact
- Show: Overall dashboard, high-level trends
- Skip: Technical implementation details
- Emphasize: ROI, decision-making speed, customer success

### For Product Managers (20 minutes)
- Focus on: Product adoption, activation rates, cross-product usage
- Show: Segment dashboard, product-specific metrics
- Include: How to define qualifying events, activation criteria
- Emphasize: Product insights, user journey, feature prioritization

### For Data Teams (30 minutes)
- Focus on: Implementation details, data models, extensibility
- Show: dbt code, state calculation logic, event schema
- Include: Live coding/query session
- Emphasize: Maintainability, scalability, data quality

### For Leadership Team (15 minutes)
- Focus on: Strategic alignment, organizational benefits
- Show: All 3 dashboard tiers, framework philosophy
- Include: Implementation timeline, resource needs
- Emphasize: Metric standardization, self-service analytics, data-driven culture

## Post-Demo Action Items

After a successful demo, suggest these next steps:

1. **Week 1**: Define pilot scope (1-2 products, 1-2 teams)
2. **Week 2-3**: Map existing events to Monstera schema
3. **Week 4-5**: Implement bronze/silver layers
4. **Week 6-7**: Build gold layer metrics and dashboards
5. **Week 8**: Training and rollout

Provide them with:
- ✅ Monstera design document
- ✅ Implementation summary
- ✅ Demo codebase
- ✅ Timeline and resource estimates
- ✅ Quick wins list (metrics to implement first)

---

## Troubleshooting Demo Issues

**Database not found:**
```bash
rm monstera_demo.duckdb
./run_demo.sh
```

**Query returns empty:**
- Check `dbt seed` ran successfully
- Verify `dbt run` completed all models
- Try `dbt run --full-refresh`

**Want to modify demo data:**
1. Edit CSV files in `seeds/`
2. Run `dbt seed --full-refresh`
3. Run `dbt run`

**Demo machine doesn't have Python:**
Use Docker:
```bash
docker run -it -v $(pwd):/project python:3.11 bash
cd /project
./run_demo.sh
```

---

**Good luck with your demo! The Monstera framework will transform how your organization thinks about metrics.**
