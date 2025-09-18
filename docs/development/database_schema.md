# 🗄️ Database Schema Documentation

## Overview

The Eclesiar application uses SQLite database for storing game data, API responses, and generated reports. The database schema is defined in `/src/data/database/models.py` and consists of 10 main tables.

## 📋 Database Configuration

- **Database Type**: SQLite 3
- **Default Path**: `data/eclesiar.db`
- **Environment Variable**: `ECLESIAR_DB_PATH`
- **WAL Mode**: Enabled for better performance
- **Foreign Keys**: Enabled

## 📊 Tables Schema

### 1. `api_snapshots` - API Response Cache

Stores raw snapshots of API responses for debugging and historical analysis.

```sql
CREATE TABLE api_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp with Z suffix
    endpoint TEXT NOT NULL,             -- API endpoint called
    payload_json TEXT NOT NULL          -- Complete JSON response
);
```

**Purpose**: Debugging, API monitoring, historical data analysis
**Usage**: Called by `save_snapshot()` function
**Data Retention**: No automatic cleanup (manual management required)

---

### 2. `item_prices` - Economic Items Price History

Time-series data for economic items prices converted to GOLD standard.

```sql
CREATE TABLE item_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,                   -- ISO 8601 timestamp
    item_id INTEGER NOT NULL,           -- Game item ID
    country_id INTEGER,                 -- Country where item is sold
    country_name TEXT,                  -- Country name for readability
    currency_id INTEGER,                -- Local currency ID
    currency_name TEXT,                 -- Local currency name
    price_original REAL,                -- Price in local currency
    price_gold REAL                     -- Price converted to GOLD
);
```

**Purpose**: Price tracking, trend analysis, economic reports
**Usage**: Called by `save_item_prices_from_cheapest()` function
**Data Source**: Market API responses processed for cheapest items
**Queries**: `get_item_price_series()`, `get_item_price_avg()`

---

### 3. `currency_rates` - Currency Exchange Rates

Historical exchange rates for all currencies relative to GOLD.

```sql
CREATE TABLE currency_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,                   -- ISO 8601 timestamp
    currency_id INTEGER NOT NULL,       -- Currency ID from game
    rate_gold_per_unit REAL NOT NULL    -- How much GOLD for 1 unit of currency
);
```

**Purpose**: Currency conversion, arbitrage analysis, economic reports
**Usage**: Called by `save_currency_rates()` function
**Data Source**: Market coin API responses
**Note**: Rate > 1 means currency is stronger than GOLD

---

### 4. `historical_reports` - Daily Reports Archive

Stores daily generated reports data for comparison and historical analysis.

```sql
CREATE TABLE historical_reports (
    date_key TEXT PRIMARY KEY,          -- YYYY-MM-DD format
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    payload_json TEXT NOT NULL          -- Complete report data as JSON
);
```

**Purpose**: Historical comparison, trend analysis, data persistence
**Usage**: Called by `save_historical_report()` and `load_historical_reports()`
**Replaces**: Legacy `historia_raportow.json` file
**Conflict Resolution**: ON CONFLICT DO UPDATE (overwrites existing dates)

---

### 5. `raw_api_cache` - Latest API Data Cache

Single-row cache for the most recent complete API dataset.

```sql
CREATE TABLE raw_api_cache (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Ensures only one row
    created_at TEXT NOT NULL,               -- ISO 8601 timestamp
    payload_json TEXT NOT NULL              -- Complete API dataset as JSON
);
```

**Purpose**: Fast data access, reducing API calls, offline mode support
**Usage**: Called by `save_raw_cache()` and `load_raw_cache()`
**Replaces**: Legacy `raw_api_output.json` file
**Constraint**: Only one row allowed (id must be 1)

---

### 6. `regions_data` - Regional Production Data

Detailed data about game regions including production bonuses and population.

```sql
CREATE TABLE regions_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    region_name TEXT NOT NULL,          -- Region name (e.g., "Warsaw")
    country_name TEXT NOT NULL,         -- Country name (e.g., "Poland")
    country_id INTEGER NOT NULL,        -- Country ID from game
    pollution REAL NOT NULL,            -- Pollution level (affects production)
    bonus_score INTEGER NOT NULL,       -- Overall bonus score
    bonus_description TEXT NOT NULL,    -- Human-readable bonus description
    bonus_by_type TEXT NOT NULL,        -- JSON object with bonuses by product type
    population INTEGER NOT NULL,        -- Region population
    nb_npcs INTEGER NOT NULL,           -- Number of NPCs in region
    type INTEGER NOT NULL,              -- Region type ID
    original_country_id INTEGER NOT NULL, -- Original country (if conquered)
    bonus_per_pollution REAL NOT NULL  -- Bonus efficiency per pollution unit
);
```

**Purpose**: Production analysis, regional comparison, efficiency calculations
**Usage**: Called by `save_regions_data()` and `load_regions_data()`
**JSON Field**: `bonus_by_type` contains `{"GRAIN": 15, "IRON": 20, ...}`
**Migration**: Has automatic column addition for `bonus_by_type`

---

### 7. `regions_summary` - Regional Data Summaries

Aggregated summary statistics for regional data.

```sql
CREATE TABLE regions_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    summary_json TEXT NOT NULL          -- Aggregated statistics as JSON
);
```

**Purpose**: Quick access to regional statistics, performance optimization
**Usage**: Called by `save_regions_data()` and `load_regions_data()`
**Content**: Aggregated data like totals, averages, rankings

---

### 8. `countries` - Countries Master Data (Repository System)

Master table for countries data in the new repository pattern.

```sql
CREATE TABLE countries (
    id INTEGER PRIMARY KEY,             -- Country ID from game
    name TEXT NOT NULL,                 -- Country name
    currency_id INTEGER NOT NULL,       -- Currency used by country
    currency_name TEXT NOT NULL,        -- Currency name
    is_available BOOLEAN DEFAULT 1     -- Whether country is active
);
```

**Purpose**: Countries reference data, repository pattern implementation
**Usage**: Part of new repository system (see `/src/data/repositories/`)
**Pattern**: Domain entity mapping for clean architecture

---

### 9. `currencies` - Currencies Master Data (Repository System)

Master table for currencies in the repository pattern.

```sql
CREATE TABLE currencies (
    id INTEGER PRIMARY KEY,             -- Currency ID from game
    name TEXT NOT NULL,                 -- Currency full name
    code TEXT NOT NULL,                 -- Currency code (e.g., "USD", "EUR")
    gold_rate REAL DEFAULT 0.0         -- Current exchange rate to GOLD
);
```

**Purpose**: Currencies reference data, repository pattern implementation
**Usage**: Part of new repository system
**Pattern**: Domain entity mapping for clean architecture

---

### 10. `regions` - Regions Master Data (Repository System)

Master table for regions in the repository pattern.

```sql
CREATE TABLE regions (
    id INTEGER PRIMARY KEY,             -- Region ID from game
    name TEXT NOT NULL,                 -- Region name
    country_id INTEGER NOT NULL,       -- Foreign key to countries
    country_name TEXT NOT NULL,        -- Country name (denormalized)
    pollution REAL DEFAULT 0.0,        -- Current pollution level
    bonus_score INTEGER DEFAULT 0,     -- Current bonus score
    population INTEGER DEFAULT 0       -- Current population
);
```

**Purpose**: Regions reference data, repository pattern implementation
**Usage**: Part of new repository system
**Pattern**: Domain entity mapping for clean architecture

## 🔄 Database Operations

### Initialization
```python
from src.data.database.models import init_db
init_db()  # Creates all tables if they don't exist
```

### Connection Management
- **WAL Mode**: Enabled for better concurrent access
- **Foreign Keys**: Enabled for data integrity
- **Row Factory**: `sqlite3.Row` for dict-like access
- **Connection**: Automatic with context managers

### Data Flow
1. **API Data** → `api_snapshots` (raw storage)
2. **Processed Data** → `raw_api_cache` (latest complete dataset)
3. **Economic Data** → `item_prices`, `currency_rates` (time series)
4. **Regional Data** → `regions_data`, `regions_summary` (production analysis)
5. **Reports** → `historical_reports` (daily archives)

## 📈 Performance Considerations

### Indexes (Recommended)
```sql
-- For time-based queries
CREATE INDEX idx_item_prices_ts ON item_prices(ts);
CREATE INDEX idx_currency_rates_ts ON currency_rates(ts);

-- For item lookups
CREATE INDEX idx_item_prices_item_id ON item_prices(item_id);
CREATE INDEX idx_currency_rates_currency_id ON currency_rates(currency_id);

-- For regional queries
CREATE INDEX idx_regions_data_country_id ON regions_data(country_id);
CREATE INDEX idx_regions_data_created_at ON regions_data(created_at);
```

### Data Retention
- **api_snapshots**: Consider periodic cleanup (>30 days)
- **item_prices**: Keep recent data for trend analysis
- **currency_rates**: Historical data valuable for arbitrage
- **raw_api_cache**: Single row, auto-updated

## 🔧 Maintenance

### Regular Tasks
1. **Vacuum**: `VACUUM;` to reclaim space
2. **Analyze**: `ANALYZE;` to update query statistics
3. **Backup**: Regular database backups
4. **Cleanup**: Remove old API snapshots

### Migrations
- Database schema changes are handled in `init_db()`
- Use `ALTER TABLE` with error handling for new columns
- Example: `bonus_by_type` column addition (lines 115-123)

## 🚨 Common Issues

### Database Locked
- Check for long-running transactions
- Ensure proper connection closing
- WAL mode reduces locking issues

### Large Database Size
- `api_snapshots` can grow large
- Implement retention policy
- Regular VACUUM operations

### JSON Field Parsing
- `bonus_by_type`, `summary_json`, `payload_json` require JSON parsing
- Handle parse errors gracefully
- Validate JSON structure before storage

## 📚 Related Files

- **Schema Definition**: `/src/data/database/models.py`
- **Repository Pattern**: `/src/data/repositories/sqlite_repository.py`
- **Domain Entities**: `/src/core/models/entities.py`
- **Repository Interfaces**: `/src/core/models/repositories.py`
- **Configuration**: `/src/core/config/app_config.py`
