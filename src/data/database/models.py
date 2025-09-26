import os
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

DB_PATH = os.getenv("ECLESIAR_DB_PATH", "data/eclesiar.db")


def _connect() -> sqlite3.Connection:

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:

    with _connect() as conn:
        cur = conn.cursor()
        # Raw snapshots of API responses
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS api_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        # Economic prices time-series (in GOLD)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS item_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                country_id INTEGER,
                country_name TEXT,
                currency_id INTEGER,
                currency_name TEXT,
                price_original REAL,
                price_gold REAL
            )
            """
        )
        # Currency rates vs GOLD
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS currency_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                currency_id INTEGER NOT NULL,
                rate_gold_per_unit REAL NOT NULL
            )
            """
        )
        # Historical reports storage (replaces historia_raportow.json)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS historical_reports (
                date_key TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        # Raw API output cache storage (replaces raw_api_output.json)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_api_cache (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        
        # Regions data storage
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS regions_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                region_name TEXT NOT NULL,
                country_name TEXT NOT NULL,
                country_id INTEGER NOT NULL,
                pollution REAL NOT NULL,
                bonus_score INTEGER NOT NULL,
                bonus_description TEXT NOT NULL,
                bonus_by_type TEXT NOT NULL,
                population INTEGER NOT NULL,
                nb_npcs INTEGER NOT NULL,
                type INTEGER NOT NULL,
                original_country_id INTEGER NOT NULL,
                bonus_per_pollution REAL NOT NULL
            )
            """
        )
        
        # Regions summary storage
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS regions_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                summary_json TEXT NOT NULL
            )
            """
        )
        
        # Migration: add bonus_by_type column if it doesn't exist
        try:
            cur.execute("ALTER TABLE regions_data ADD COLUMN bonus_by_type TEXT DEFAULT '{}'")
            print("Added bonus_by_type column to regions_data table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("bonus_by_type column already exists")
            else:
                print(f"Error adding bonus_by_type column: {e}")
        
        # Add new tables for repository system
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                currency_id INTEGER NOT NULL,
                currency_name TEXT NOT NULL,
                is_available BOOLEAN DEFAULT 1
            )
            """
        )
        
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS currencies (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                gold_rate REAL DEFAULT 0.0
            )
            """
        )
        
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country_id INTEGER NOT NULL,
                country_name TEXT NOT NULL,
                pollution REAL DEFAULT 0.0,
                bonus_score INTEGER DEFAULT 0,
                population INTEGER DEFAULT 0
            )
            """
        )
        
        conn.commit()


def save_snapshot(endpoint: str, payload: Dict[str, Any]) -> None:

    ts = datetime.utcnow().isoformat() + "Z"
    with _connect() as conn:
        conn.execute(
            "INSERT INTO api_snapshots(created_at, endpoint, payload_json) VALUES(?,?,?)",
            (ts, endpoint, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()


def save_currency_rates(rates_map: Dict[Any, Any]) -> None:

    if not rates_map:
        return
    ts = datetime.utcnow().isoformat() + "Z"
    rows: List[Tuple[str, float]] = []
    for cid, rate in rates_map.items():
        try:
            cid_int = int(cid)
        except Exception:
            # Keep string IDs as-is by hashing to int domain not necessary; store as NULL and name in country_name if needed.
            # But for simplicity, skip non-int ids here.
            continue
        try:
            rate_val = float(rate)
        except Exception:
            continue
        rows.append((ts, cid_int, rate_val))
    if not rows:
        return
    with _connect() as conn:
        conn.executemany(
            "INSERT INTO currency_rates(ts, currency_id, rate_gold_per_unit) VALUES(?,?,?)",
            rows,
        )
        conn.commit()


def save_item_prices_from_cheapest(cheapest_by_item: Dict[Any, List[Dict[str, Any]]]) -> None:

    if not cheapest_by_item:
        return
    ts = datetime.utcnow().isoformat() + "Z"
    rows: List[Tuple[str, int, Optional[int], Optional[str], Optional[int], Optional[str], Optional[float], Optional[float]]] = []
    for item_id, entries in cheapest_by_item.items():
        try:
            item_id_int = int(item_id)
        except Exception:
            continue
        if not entries:
            continue
        # Save top offer (cheapest)
        e = entries[0]
        country_id = e.get("country_id")
        country_name = e.get("country_name") or e.get("country")
        currency_id = e.get("currency_id")
        currency_name = e.get("currency_name")
        price_original = e.get("price_in_currency") or e.get("price_currency")
        price_gold = e.get("price_in_gold") or e.get("price_gold")
        try:
            price_original_f = float(price_original) if price_original is not None else None
        except Exception:
            price_original_f = None
        try:
            price_gold_f = float(price_gold) if price_gold is not None else None
        except Exception:
            price_gold_f = None
        rows.append(
            (
                ts,
                item_id_int,
                int(country_id) if country_id is not None else None,
                str(country_name) if country_name is not None else None,
                int(currency_id) if currency_id is not None else None,
                str(currency_name) if currency_name is not None else None,
                price_original_f,
                price_gold_f,
            )
        )
    if not rows:
        return
    with _connect() as conn:
        conn.executemany(
            """
            INSERT INTO item_prices(
                ts, item_id, country_id, country_name, currency_id, currency_name, price_original, price_gold
            ) VALUES(?,?,?,?,?,?,?,?)
            """,
            rows,
        )
        conn.commit()


def get_item_price_series(item_id: int, limit: int = 90) -> List[Tuple[str, Optional[float]]]:

    with _connect() as conn:
        cur = conn.execute(
            """
            SELECT ts, price_gold
            FROM item_prices
            WHERE item_id = ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (item_id, limit),
        )
        rows = cur.fetchall()
    # Return ascending time order
    return [(r["ts"], r["price_gold"]) for r in reversed(rows)]


def get_item_price_avg(item_id: int, days: int = 30) -> Optional[float]:

    with _connect() as conn:
        cur = conn.execute(
            """
            SELECT AVG(price_gold) as avg_price
            FROM (
                SELECT price_gold
                FROM item_prices
                WHERE item_id = ? AND price_gold IS NOT NULL
                ORDER BY ts DESC
                LIMIT ?
            )
            """,
            (item_id, days),
        )
        row = cur.fetchone()
        if not row:
            return None
        return float(row["avg_price"]) if row["avg_price"] is not None else None


def save_historical_report(date_key: str, payload: Dict[str, Any]) -> None:

    ts = datetime.utcnow().isoformat() + "Z"
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO historical_reports(date_key, created_at, payload_json)
            VALUES(?,?,?)
            ON CONFLICT(date_key) DO UPDATE SET
                created_at=excluded.created_at,
                payload_json=excluded.payload_json
            """,
            (date_key, ts, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()


def load_historical_reports() -> Dict[str, Any]:

    with _connect() as conn:
        cur = conn.execute(
            "SELECT date_key, payload_json FROM historical_reports"
        )
        rows = cur.fetchall()
    out: Dict[str, Any] = {}
    for r in rows:
        try:
            out[str(r["date_key"]) ] = json.loads(r["payload_json"])
        except Exception:
            continue
    return out


def save_raw_cache(payload: Dict[str, Any]) -> None:

    ts = datetime.utcnow().isoformat() + "Z"
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO raw_api_cache(id, created_at, payload_json)
            VALUES(1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                created_at=excluded.created_at,
                payload_json=excluded.payload_json
            """,
            (ts, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()


def load_raw_cache() -> Optional[Dict[str, Any]]:

    with _connect() as conn:
        cur = conn.execute("SELECT payload_json FROM raw_api_cache WHERE id = 1")
        row = cur.fetchone()
    if not row:
        return None
    try:
        return json.loads(row["payload_json"])
    except Exception:
        return None


def load_regions_data() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Loads region data from the database.
    
    Returns:
        Tuple (list of regions, summary)
    """
    try:
        with _connect() as conn:
            # Get the latest summary
            cursor = conn.execute(
                """
                SELECT summary_json FROM regions_summary 
                ORDER BY created_at DESC LIMIT 1
                """
            )
            summary_row = cursor.fetchone()
            summary = json.loads(summary_row[0]) if summary_row else {}
            
            # Get the latest region data
            cursor = conn.execute(
                """
                SELECT region_name, country_name, country_id, pollution, 
                       bonus_score, bonus_description, bonus_by_type, population, nb_npcs, 
                       type, original_country_id, bonus_per_pollution
                FROM regions_data 
                ORDER BY created_at DESC 
                LIMIT 1000
                """
            )
            
            regions_data = []
            for row in cursor.fetchall():
                region = {
                    'region_name': row[0],
                    'country_name': row[1],
                    'country_id': row[2],
                    'pollution': row[3],
                    'bonus_score': row[4],
                    'bonus_description': row[5],
                    'bonus_by_type': json.loads(row[6]) if row[6] else {},
                    'population': row[7],
                    'nb_npcs': row[8],
                    'type': row[9],
                    'original_country_id': row[10],
                    'bonus_per_pollution': row[11]
                }
                regions_data.append(region)
            
            return regions_data, summary
            
    except Exception as e:
        print(f"Error loading region data from database: {e}")
        return [], {}


def save_regions_data(regions_data: List[Dict[str, Any]], regions_summary: Dict[str, Any]) -> None:
    """
    Saves region data to the database.
    
    Args:
        regions_data: List of regions with bonuses
        regions_summary: Summary of region data
    """
    ts = datetime.utcnow().isoformat() + "Z"
    
    with _connect() as conn:
        # Save summary
        conn.execute(
            """
            INSERT INTO regions_summary(created_at, summary_json)
            VALUES(?,?)
            """,
            (ts, json.dumps(regions_summary, ensure_ascii=False)),
        )
        
        # Save detailed region data
        for region in regions_data:
            conn.execute(
                """
                INSERT INTO regions_data(
                    created_at, region_name, country_name, country_id, 
                    pollution, bonus_score, bonus_description, bonus_by_type, population, 
                    nb_npcs, type, original_country_id, bonus_per_pollution
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    ts,
                    region.get('region_name', ''),
                    region.get('country_name', ''),
                    region.get('country_id', 0),
                    region.get('pollution', 0.0),
                    region.get('bonus_score', 0),
                    region.get('bonus_description', ''),
                    json.dumps(region.get('bonus_by_type', {}), ensure_ascii=False),
                    region.get('population', 0),
                    region.get('nb_npcs', 0),
                    region.get('type', 0),
                    region.get('original_country_id', 0),
                    region.get('bonus_per_pollution', 0.0)
                ),
            )
        
        conn.commit()



