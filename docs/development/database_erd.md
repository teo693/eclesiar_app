# 📊 Database Entity Relationship Diagram

## Visual Schema Overview

```mermaid
erDiagram
    api_snapshots {
        integer id PK
        text created_at
        text endpoint
        text payload_json
    }
    
    countries {
        integer id PK
        text name
        integer currency_id FK
        text currency_name
        boolean is_available
    }
    
    currencies {
        integer id PK
        text name
        text code
        real gold_rate
    }
    
    item_prices {
        integer id PK
        text ts
        integer item_id
        integer country_id FK
        text country_name
        integer currency_id FK
        text currency_name
        real price_original
        real price_gold
    }
    
    currency_rates {
        integer id PK
        text ts
        integer currency_id FK
        real rate_gold_per_unit
    }
    
    regions {
        integer id PK
        text name
        integer country_id FK
        text country_name
        real pollution
        integer bonus_score
        integer population
    }
    
    regions_data {
        integer id PK
        text created_at
        text region_name
        text country_name
        integer country_id FK
        real pollution
        integer bonus_score
        text bonus_description
        integer population
        integer nb_npcs
        integer type
        integer original_country_id
        real bonus_per_pollution
        text bonus_by_type
    }
    
    regions_summary {
        integer id PK
        text created_at
        text summary_json
    }
    
    historical_reports {
        text date_key PK
        text created_at
        text payload_json
    }
    
    raw_api_cache {
        integer id PK
        text created_at
        text payload_json
    }

    %% Relationships
    countries ||--o{ item_prices : "has prices"
    currencies ||--o{ currency_rates : "has rates"
    currencies ||--o{ item_prices : "priced in"
    countries ||--o{ regions : "contains"
    countries ||--o{ regions_data : "has detailed data"
```

## 🔗 Key Relationships

### **Primary Relationships:**
- `countries` ↔ `currencies` (1:1) - Each country has one currency
- `countries` → `regions` (1:N) - Countries contain multiple regions  
- `countries` → `item_prices` (1:N) - Countries have item prices
- `currencies` → `currency_rates` (1:N) - Currencies have historical rates

### **Data Flow:**
1. **Countries & Currencies** → Static reference data
2. **API Snapshots** → Raw API responses (cache)
3. **Item Prices** → Economic data over time
4. **Currency Rates** → Exchange rates over time
5. **Regions** → Geographic/political data
6. **Reports** → Generated analysis results

## 📋 Table Categories

### **🏛️ Reference Data (Static)**
- `countries` - Country definitions
- `currencies` - Currency definitions  
- `regions` - Basic region info

### **📊 Time Series Data**
- `item_prices` - Economic prices over time
- `currency_rates` - Exchange rates over time
- `regions_data` - Detailed region data snapshots

### **💾 Cache & Storage**
- `api_snapshots` - Raw API response cache
- `raw_api_cache` - Latest complete data dump
- `historical_reports` - Generated report archive
- `regions_summary` - Processed region summaries

## 🎯 Usage Patterns

### **For Developers:**
- Start with `countries` and `currencies` for reference data
- Use `item_prices` and `currency_rates` for economic analysis
- Check `api_snapshots` for debugging API issues
- Store analysis results in `historical_reports`
