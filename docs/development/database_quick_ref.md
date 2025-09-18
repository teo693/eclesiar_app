# 🚀 Database Quick Reference

## Essential Commands for Developers

### **🔍 Inspect Database**
```bash
# Quick overview
python docs/development/database_setup.py

# SQLite CLI
sqlite3 data/eclesiar.db

# Show all tables
.tables

# Describe table structure  
.schema table_name

# Show data
SELECT * FROM table_name LIMIT 10;
```

### **📊 Key Tables Cheat Sheet**

| Table | Purpose | Key Fields | Records |
|-------|---------|------------|---------|
| `countries` | Reference data | `id`, `name`, `currency_id` | ~50 |
| `currencies` | Currency definitions | `id`, `name`, `code`, `gold_rate` | ~50 |
| `item_prices` | Economic data | `item_id`, `country_id`, `price_gold` | 1000s |
| `currency_rates` | Exchange rates | `currency_id`, `rate_gold_per_unit` | 1000s |
| `api_snapshots` | API cache | `endpoint`, `payload_json` | 100s |
| `regions` | Geographic data | `country_id`, `name`, `pollution` | 100s |

### **🎯 Common Queries**

```sql
-- Latest currency rates
SELECT c.name, cr.rate_gold_per_unit, cr.ts
FROM currencies c 
JOIN currency_rates cr ON c.id = cr.currency_id
WHERE cr.ts = (SELECT MAX(ts) FROM currency_rates WHERE currency_id = c.id);

-- Item prices by country
SELECT country_name, item_id, price_gold 
FROM item_prices 
WHERE ts = (SELECT MAX(ts) FROM item_prices)
ORDER BY price_gold DESC;

-- Recent API activity
SELECT created_at, endpoint, LENGTH(payload_json) as size
FROM api_snapshots 
ORDER BY created_at DESC 
LIMIT 10;

-- Countries with their currencies
SELECT c.name as country, curr.name as currency, curr.code
FROM countries c
JOIN currencies curr ON c.currency_id = curr.id;
```

### **⚡ Development Tips**

1. **Database Location**: `data/eclesiar.db`
2. **Schema Definition**: `src/data/database/models.py`
3. **Initialization**: Run app once to create tables
4. **Backup**: Copy `.db` file before experiments
5. **Reset**: Delete `.db` file to recreate from scratch

### **🔧 Useful Functions**

```python
# In your Python code
from src.data.database.connection import get_db_connection

# Get connection
conn = get_db_connection()

# Safe query execution
from src.data.database.models import execute_safe_query
result = execute_safe_query(conn, "SELECT * FROM countries")
```

### **📱 Environment Variables**

```bash
# Override database path
export ECLESIAR_DB_PATH="/custom/path/to/database.db"

# Enable SQL logging (development)
export ECLESIAR_DEBUG_SQL=1
```
