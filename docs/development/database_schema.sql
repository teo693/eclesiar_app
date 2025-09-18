CREATE TABLE api_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE item_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                country_id INTEGER,
                country_name TEXT,
                currency_id INTEGER,
                currency_name TEXT,
                price_original REAL,
                price_gold REAL
            );
CREATE TABLE currency_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                currency_id INTEGER NOT NULL,
                rate_gold_per_unit REAL NOT NULL
            );
CREATE TABLE historical_reports (
                date_key TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
CREATE TABLE raw_api_cache (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
CREATE TABLE regions_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                region_name TEXT NOT NULL,
                country_name TEXT NOT NULL,
                country_id INTEGER NOT NULL,
                pollution REAL NOT NULL,
                bonus_score INTEGER NOT NULL,
                bonus_description TEXT NOT NULL,
                population INTEGER NOT NULL,
                nb_npcs INTEGER NOT NULL,
                type INTEGER NOT NULL,
                original_country_id INTEGER NOT NULL,
                bonus_per_pollution REAL NOT NULL
            , bonus_by_type TEXT DEFAULT '{}');
CREATE TABLE regions_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                summary_json TEXT NOT NULL
            );
CREATE TABLE countries (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                currency_id INTEGER NOT NULL,
                currency_name TEXT NOT NULL,
                is_available BOOLEAN DEFAULT 1
            );
CREATE TABLE currencies (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                gold_rate REAL DEFAULT 0.0
            );
CREATE TABLE regions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country_id INTEGER NOT NULL,
                country_name TEXT NOT NULL,
                pollution REAL DEFAULT 0.0,
                bonus_score INTEGER DEFAULT 0,
                population INTEGER DEFAULT 0
            );
