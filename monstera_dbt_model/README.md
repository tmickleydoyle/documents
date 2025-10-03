# Monstera Metrics Framework - DBT Implementation

A complete implementation of the Monstera Company Metrics Design framework using dbt (data build tool).

## 🎯 What is This?

This is a working demo of the **Monstera metrics framework** - a comprehensive approach to:
- **User Lifecycle States** (8 states: new, active, dormant, churned, etc.)
- **Product Taxonomy** (4-tier hierarchy of products and features)
- **Account Health** (B2B lifecycle states and health scoring)
- **Cross-Product Analytics** (adoption patterns, multi-product usage)
- **Behavioral Segmentation** (engagement levels, journey stages)

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Run the demo setup script
./run_demo.sh

# 2. Query your metrics
duckdb monstera_demo.duckdb -c "SELECT * FROM silver.silver_user_current_state;"

# 3. Export to CSV for visualization
./export_demo_data.sh

# 4. Check out the exports
open exports/
```

That's it! You now have a working metrics system with:
- 20 users across 10 accounts
- 40 events across 5 products
- Complete lifecycle state calculations
- Product adoption metrics
- Account health scores

## 📊 What You'll See

### User Lifecycle States
```sql
-- View user state distribution
SELECT platform_state, COUNT(*) as users
FROM silver.silver_user_current_state
GROUP BY 1;
```

Example output:
```
platform_state | users
---------------|------
active         |   8
new            |   4
dormant        |   3
churned        |   5
```

### Product Adoption
```sql
-- View product adoption rates
SELECT product_name, users_active, activation_rate_pct
FROM (demo query - see demo_queries.sql)
```

Example output:
```
product_name    | users_active | activation_rate_pct
----------------|--------------|--------------------
Video Editor    |     12       |      85.7
Template Library|      6       |      60.0
Team Workspace  |      3       |      75.0
```

### Account Health
```sql
-- View account health distribution
SELECT current_state, COUNT(*), AVG(health_score)
FROM silver.silver_account_current_state
GROUP BY 1;
```

Example output:
```
current_state | count | avg_health_score
--------------|-------|------------------
active        |   5   |      72.3
expanding     |   2   |      85.1
at_risk       |   2   |      35.8
trial         |   1   |      15.0
```

## 📁 Project Structure

```
monstera_dbt_model/
├── seeds/                          # Mock data (CSV files)
│   ├── seed_accounts.csv           # 10 sample accounts
│   ├── seed_users.csv              # 20 sample users
│   ├── seed_events.csv             # 40 sample events
│   └── seed_product_catalog.csv    # Product taxonomy
│
├── models/
│   ├── bronze/                     # Raw data layer
│   │   ├── bronze_events.sql       # Events with product attribution
│   │   ├── bronze_users.sql        # User entity data
│   │   ├── bronze_accounts.sql     # Account entity data
│   │   └── bronze_product_catalog.sql
│   │
│   ├── silver/                     # Business logic layer
│   │   ├── silver_user_current_state.sql        # User lifecycle states
│   │   ├── silver_user_product_states.sql       # Product-specific states
│   │   └── silver_account_current_state.sql     # Account health & states
│   │
│   └── gold/                       # Aggregated metrics layer
│       ├── gold_users_active_monthly.sql        # MAU calculation
│       ├── gold_overall_metrics.sql             # Overall dashboard
│       └── gold_segment_metrics.sql             # Segment dashboard
│
├── demo_queries.sql                # Pre-built queries for demo
├── run_demo.sh                     # One-command setup script
├── export_demo_data.sh             # Export to CSV for viz
├── QUICKSTART_DEMO.md              # Detailed setup guide
└── MONSTERA_IMPLEMENTATION_SUMMARY.md  # Complete implementation docs
```

## 🎨 Creating a Demo Dashboard

### Option 1: Spreadsheet (Easiest)

1. Run `./export_demo_data.sh`
2. Open `exports/user_states.csv` in Excel/Google Sheets
3. Create charts:
   - **Pie Chart**: User state distribution
   - **Line Chart**: MAU trend over time
   - **Bar Chart**: Product adoption rates
   - **Gauge**: Account health scores

### Option 2: Metabase (Best Visual Demo)

```bash
# Start Metabase
docker run -d -p 3000:3000 --name metabase metabase/metabase

# Open http://localhost:3000
# Connect to: monstera_demo.duckdb
# Create dashboards using demo_queries.sql
```

### Option 3: Evidence.dev (Code-Based BI)

```bash
npm install -g @evidence-dev/evidence
npx degit evidence-dev/template monstera-dashboard
cd monstera-dashboard
# Update connection.yaml with DuckDB path
npm run dev
```

## 📈 Key Metrics Demonstrated

### 1. User Lifecycle Metrics
- **Monthly Active Users (MAU)** - by country, plan type
- **User State Distribution** - new/active/dormant/churned
- **Activation Rates** - % of new users who activate
- **Retention Curves** - by cohort, segment

### 2. Product Metrics
- **Product Adoption Rates** - % of users trying each product
- **Product Activation Rates** - % of users completing activation
- **Multi-Product Usage** - users active in 2+, 3+ products
- **Product State Distribution** - per-product lifecycle states

### 3. Account Health Metrics (B2B)
- **Account State Distribution** - trial/active/at-risk/churned
- **Health Scores** - 0-100 composite score
- **Seat Utilization** - active users / total seats
- **MRR Tracking** - by account state

### 4. Cross-Product Analytics
- **Product Affinity** - which products are used together
- **Adoption Sequences** - order of product adoption
- **Cross-Product Retention** - single vs multi-product users

## 🔧 Customizing the Demo

### Add More Users

Edit `seeds/seed_users.csv` and add rows:
```csv
usr_021,newuser@example.com,acc_001,2024-12-01,US,enterprise,organic
```

Then run:
```bash
dbt seed --full-refresh
dbt run
```

### Add More Events

Edit `seeds/seed_events.csv`:
```csv
evt_041,usr_001,user,video_created,2024-12-15 10:00:00,web_app,sess_013,video_editor,true,true,{}
```

### Change Time Windows

Edit `models/silver/silver_user_current_state.sql` and modify:
```sql
WHEN DATEDIFF('day', u.user_created_at, CURRENT_DATE) <= 30  -- Change to 60 for longer new period
```

## 📖 Documentation

- **[QUICKSTART_DEMO.md](QUICKSTART_DEMO.md)** - Complete setup guide with multiple DB options
- **[MONSTERA_IMPLEMENTATION_SUMMARY.md](MONSTERA_IMPLEMENTATION_SUMMARY.md)** - Full implementation details
- **[demo_queries.sql](demo_queries.sql)** - 30+ pre-built queries
- **[Monstera_Company_Metric_Design.md](../Monstera_Company_Metric_Design.md)** - Framework philosophy

## 🎓 Learning Path

1. **Start Here**: Run `./run_demo.sh` and explore the data
2. **Understand States**: Query `silver.silver_user_current_state`
3. **Explore Products**: Query product adoption metrics
4. **Check Accounts**: Review account health scores
5. **Visualize**: Export CSVs and create charts
6. **Customize**: Modify seed data for your use case
7. **Extend**: Add new metrics following Monstera patterns

## 💡 Demo Tips

### For Product Managers
Focus on:
- Product adoption funnels
- Activation rates by product
- Multi-product usage patterns
- User lifecycle progression

### For Executives
Focus on:
- MAU trends
- Account health distribution
- MRR by account state
- High-level user state distribution

### For Data Teams
Focus on:
- Event schema compliance
- State calculation logic
- Data quality tests
- Metric naming conventions

## 🐛 Troubleshooting

**"Relation not found" errors**
```bash
dbt seed --full-refresh
dbt run --full-refresh
```

**Want to start fresh?**
```bash
rm monstera_demo.duckdb
./run_demo.sh
```

**Need more sample data?**
- Edit the seed CSV files
- Run `dbt seed --full-refresh`
- Run `dbt run`

## 🤝 Contributing

This is a demo implementation. To extend:

1. Add new products to `seed_product_catalog.csv`
2. Add qualifying events for each product
3. Create product-specific activation criteria
4. Build new gold layer metrics following naming conventions
5. Document everything in schema.yml files

## 📄 License

This is a demonstration of the Monstera metrics framework for internal use.

## 🙋 Questions?

See the detailed guides:
- Setup issues → QUICKSTART_DEMO.md
- Implementation details → MONSTERA_IMPLEMENTATION_SUMMARY.md
- Framework concepts → ../Monstera_Company_Metric_Design.md

---

**Built with** ❤️ **using dbt and the Monstera framework**
