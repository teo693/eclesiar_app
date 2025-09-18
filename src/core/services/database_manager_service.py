"""
Database Manager Service

Centralny serwis do zarządzania bazą danych zgodnie z planem refaktoryzacji.
Implementuje przepływ: aktualizacja DB → generowanie raportów z DB.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.data.database.models import init_db, save_snapshot
from src.data.api.client import fetch_data
from src.core.services.economy_service import (
    fetch_countries_and_currencies,
    build_currency_rates_map,
    fetch_country_statistics,
    get_lowest_npc_wage_countries,
    fetch_cheapest_items_from_all_countries,
    fetch_best_jobs_from_all_countries
)
from src.core.services.regions_service import fetch_and_process_regions
from src.core.services.military_service import process_hits_data, build_wars_summary
from config.settings.base import AUTH_TOKEN, GOLD_ID_FALLBACK


class DatabaseManagerService:
    """Centralny serwis do zarządzania bazą danych i przepływem danych"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("ECLESIAR_DB_PATH", "data/eclesiar.db")
        self._ensure_db_initialized()
    
    def _ensure_db_initialized(self):
        """Zapewnia że baza danych jest zainicjalizowana"""
        try:
            init_db()
            self._create_additional_tables()
            print("🗄️ Database initialized")
        except Exception as e:
            print(f"⚠️ Warning: database initialization failed: {e}")
    
    def _create_additional_tables(self):
        """Tworzy dodatkowe tabele potrzebne do Database-First approach"""
        with self._connect() as conn:
            # Tabela oferuje pracy
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    country_id INTEGER NOT NULL,
                    country_name TEXT NOT NULL,
                    wage_original REAL NOT NULL,
                    wage_gold REAL NOT NULL,
                    currency_id INTEGER NOT NULL,
                    currency_name TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    business_name TEXT NOT NULL
                )
            """)
            
            # Tabela oferty rynkowe
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    country_id INTEGER NOT NULL,
                    country_name TEXT NOT NULL,
                    price_original REAL NOT NULL,
                    price_gold REAL NOT NULL,
                    currency_id INTEGER NOT NULL,
                    currency_name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    offer_type TEXT DEFAULT 'SELL'
                )
            """)
            
            # Tabela dane militarne
            conn.execute("""
                CREATE TABLE IF NOT EXISTS military_hits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    hits_data_json TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS military_wars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    wars_summary_json TEXT NOT NULL
                )
            """)
            
            # Tabela ranking wojowników
            conn.execute("""
                CREATE TABLE IF NOT EXISTS warriors_ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    warriors_data_json TEXT NOT NULL
                )
            """)
            
            # Tabela ostatniego odświeżenia
            conn.execute("""
                CREATE TABLE IF NOT EXISTS last_refresh (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def _connect(self) -> sqlite3.Connection:
        """Tworzy połączenie z bazą danych"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn
    
    def update_database_full(self, sections: Dict[str, bool] = None) -> bool:
        """
        Kompletna aktualizacja bazy danych ze wszystkimi danymi potrzebnymi do raportów.
        
        Args:
            sections: Sekcje do zaktualizowania
            
        Returns:
            True jeśli aktualizacja się powiodła, False w przeciwnym razie
        """
        if sections is None:
            sections = {
                'military': True,
                'warriors': True, 
                'economic': True,
                'production': True
            }
        
        print("🔄 Starting full database update...")
        success = True
        
        try:
            # 1. Aktualizuj dane ekonomiczne
            if sections.get('economic', False):
                print("💰 Updating economic data...")
                if not self._update_economic_data():
                    success = False
            
            # 2. Aktualizuj dane regionów (dla produktywności)
            if sections.get('production', False):
                print("🏭 Updating regions data...")
                if not self._update_regions_data():
                    success = False
            
            # 3. Aktualizuj dane militarne
            if sections.get('military', False):
                print("⚔️ Updating military data...")
                if not self._update_military_data():
                    success = False
            
            # 4. Aktualizuj dane wojowników
            if sections.get('warriors', False):
                print("🏆 Updating warriors data...")
                if not self._update_warriors_data():
                    success = False
            
            # 5. Zapisz timestamp ostatniej aktualizacji
            self._update_last_refresh_timestamp()
            
            if success:
                print("✅ Database update completed successfully")
            else:
                print("⚠️ Database update completed with some errors")
                
        except Exception as e:
            print(f"❌ Error during database update: {e}")
            success = False
        
        return success
    
    def _update_economic_data(self) -> bool:
        """Aktualizuje dane ekonomiczne w bazie danych"""
        try:
            # Pobierz kraje i waluty
            eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
            
            # Zapisz kraje
            self._save_countries_data(eco_countries, currencies_map)
            
            # Zapisz waluty
            self._save_currencies_data(currencies_map, currency_codes_map)
            
            # Pobierz i zapisz kursy walut
            currency_rates = build_currency_rates_map(currencies_map, gold_id)
            self._save_currency_rates(currency_rates)
            
            # Pobierz i zapisz najlepsze oferty pracy
            best_jobs = fetch_best_jobs_from_all_countries(eco_countries, currency_rates, gold_id)
            self._save_job_offers(best_jobs)
            
            # Pobierz i zapisz najtańsze przedmioty
            from src.core.services.economy_service import fetch_items_by_type
            items_map = fetch_items_by_type("economic")
            cheapest_items = fetch_cheapest_items_from_all_countries(eco_countries, items_map, currency_rates, gold_id)
            self._save_market_offers(cheapest_items, items_map)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating economic data: {e}")
            return False
    
    def _update_regions_data(self) -> bool:
        """Aktualizuje dane regionów w bazie danych"""
        try:
            # Pobierz kraje jeśli nie ma ich w bazie
            eco_countries = self._get_countries_from_db()
            if not eco_countries:
                eco_countries, _, _, _ = fetch_countries_and_currencies()
            
            # Pobierz i zapisz dane regionów
            regions_data, regions_summary = fetch_and_process_regions(eco_countries)
            self._save_regions_data(regions_data, regions_summary)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating regions data: {e}")
            return False
    
    def _update_military_data(self) -> bool:
        """Aktualizuje dane militarne w bazie danych"""
        try:
            # Pobierz dane o walkach
            hits_response = fetch_data("fights/hits", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            hits_data = process_hits_data(hits_response)
            
            # Pobierz dane o wojnach
            wars_response = fetch_data("fights/wars", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            wars_summary = build_wars_summary(wars_response)
            
            # Zapisz dane militarne
            self._save_military_data(hits_data, wars_summary)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating military data: {e}")
            return False
    
    def _update_warriors_data(self) -> bool:
        """Aktualizuje dane wojowników w bazie danych"""
        try:
            # Pobierz ranking wojowników
            warriors_response = fetch_data("citizens/top", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            
            # Zapisz dane wojowników
            self._save_warriors_data(warriors_response)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating warriors data: {e}")
            return False
    
    def _save_countries_data(self, countries: List[Dict], currencies_map: Dict):
        """Zapisuje dane krajów do bazy danych"""
        with self._connect() as conn:
            # Wyczyść starą tabelę
            conn.execute("DELETE FROM countries")
            
            # Wstaw nowe dane
            for country in countries:
                conn.execute("""
                    INSERT OR REPLACE INTO countries 
                    (id, name, currency_id, currency_name, is_available)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    country['country_id'],
                    country['country_name'],
                    country['currency_id'],
                    currencies_map.get(country['currency_id'], 'Unknown'),
                    True
                ))
            conn.commit()
    
    def _save_currencies_data(self, currencies_map: Dict, currency_codes_map: Dict):
        """Zapisuje dane walut do bazy danych"""
        with self._connect() as conn:
            # Wyczyść starą tabelę
            conn.execute("DELETE FROM currencies")
            
            # Wstaw nowe dane
            for currency_id, currency_name in currencies_map.items():
                currency_code = currency_codes_map.get(currency_id, currency_name[:3].upper())
                conn.execute("""
                    INSERT OR REPLACE INTO currencies 
                    (id, name, code, gold_rate)
                    VALUES (?, ?, ?, ?)
                """, (currency_id, currency_name, currency_code, 0.0))
            conn.commit()
    
    def _save_currency_rates(self, currency_rates: Dict):
        """Zapisuje kursy walut do bazy danych"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wyczyść stare kursy (starsze niż 1 dzień)
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            conn.execute("DELETE FROM currency_rates WHERE ts < ?", (cutoff,))
            
            # Wstaw nowe kursy
            for currency_id, rate in currency_rates.items():
                if rate > 0:  # Tylko prawidłowe kursy
                    conn.execute("""
                        INSERT INTO currency_rates (ts, currency_id, rate_gold_per_unit)
                        VALUES (?, ?, ?)
                    """, (ts, currency_id, rate))
                    
                    # Aktualizuj również tabelę currencies
                    conn.execute("""
                        UPDATE currencies SET gold_rate = ? WHERE id = ?
                    """, (rate, currency_id))
            
            conn.commit()
    
    def _save_job_offers(self, job_offers: List[Dict]):
        """Zapisuje oferty pracy do bazy danych"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wyczyść stare oferty (starsze niż 1 dzień)
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            conn.execute("DELETE FROM job_offers WHERE ts < ?", (cutoff,))
            
            # Wstaw nowe oferty
            for job in job_offers:
                conn.execute("""
                    INSERT INTO job_offers 
                    (ts, country_id, country_name, wage_original, wage_gold, 
                     currency_id, currency_name, job_title, business_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ts,
                    job.get('country_id', 0),
                    job.get('country_name', ''),
                    job.get('wage_original', 0),
                    job.get('wage_gold', 0),
                    job.get('currency_id', 0),
                    job.get('currency_name', ''),
                    job.get('job_title', ''),
                    job.get('business_name', '')
                ))
            
            conn.commit()
    
    def _save_market_offers(self, market_offers: List[Dict], items_map: Dict):
        """Zapisuje oferty rynkowe do bazy danych"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wyczyść stare oferty (starsze niż 1 dzień)
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            conn.execute("DELETE FROM market_offers WHERE ts < ?", (cutoff,))
            
            # Wstaw nowe oferty
            for offer in market_offers:
                conn.execute("""
                    INSERT INTO market_offers 
                    (ts, item_id, item_name, country_id, country_name, 
                     price_original, price_gold, currency_id, currency_name, quantity, offer_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ts,
                    offer.get('item_id', 0),
                    offer.get('item_name', ''),
                    offer.get('country_id', 0),
                    offer.get('country_name', ''),
                    offer.get('price_original', 0),
                    offer.get('price_gold', 0),
                    offer.get('currency_id', 0),
                    offer.get('currency_name', ''),
                    offer.get('quantity', 1),
                    'SELL'
                ))
            
            conn.commit()
    
    def _save_regions_data(self, regions_data: List[Dict], regions_summary: Dict):
        """Zapisuje dane regionów do bazy danych"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wyczyść stare dane regionów (starsze niż 1 dzień)
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            conn.execute("DELETE FROM regions_data WHERE created_at < ?", (cutoff,))
            conn.execute("DELETE FROM regions_summary WHERE created_at < ?", (cutoff,))
            
            # Wstaw nowe dane regionów
            for region in regions_data:
                bonus_by_type_json = json.dumps(region.get('bonus_by_type', {}))
                conn.execute("""
                    INSERT INTO regions_data 
                    (created_at, region_name, country_name, country_id, pollution, 
                     bonus_score, bonus_description, bonus_by_type, population, 
                     nb_npcs, type, original_country_id, bonus_per_pollution)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ts,
                    region.get('region_name', ''),
                    region.get('country_name', ''),
                    region.get('country_id', 0),
                    region.get('pollution', 0.0),
                    region.get('bonus_score', 0),
                    region.get('bonus_description', ''),
                    bonus_by_type_json,
                    region.get('population', 0),
                    region.get('nb_npcs', 0),
                    region.get('type', 0),
                    region.get('original_country_id', 0),
                    region.get('bonus_per_pollution', 0.0)
                ))
            
            # Wstaw podsumowanie regionów
            conn.execute("""
                INSERT INTO regions_summary (created_at, summary_json)
                VALUES (?, ?)
            """, (ts, json.dumps(regions_summary)))
            
            conn.commit()
    
    def _save_military_data(self, hits_data: List[Dict], wars_summary: Dict):
        """Zapisuje dane militarne do bazy danych"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wyczyść stare dane (starsze niż 1 dzień)
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            conn.execute("DELETE FROM military_hits WHERE ts < ?", (cutoff,))
            conn.execute("DELETE FROM military_wars WHERE ts < ?", (cutoff,))
            
            # Wstaw nowe dane
            conn.execute("""
                INSERT INTO military_hits (ts, hits_data_json)
                VALUES (?, ?)
            """, (ts, json.dumps(hits_data)))
            
            conn.execute("""
                INSERT INTO military_wars (ts, wars_summary_json)
                VALUES (?, ?)
            """, (ts, json.dumps(wars_summary)))
            
            conn.commit()
    
    def _save_warriors_data(self, warriors_data: List[Dict]):
        """Zapisuje dane wojowników do bazy danych"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wyczyść stare dane (starsze niż 1 dzień)
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
            conn.execute("DELETE FROM warriors_ranking WHERE ts < ?", (cutoff,))
            
            # Wstaw nowe dane
            conn.execute("""
                INSERT INTO warriors_ranking (ts, warriors_data_json)
                VALUES (?, ?)
            """, (ts, json.dumps(warriors_data)))
            
            conn.commit()
    
    def _update_last_refresh_timestamp(self):
        """Aktualizuje timestamp ostatniego odświeżenia"""
        with self._connect() as conn:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Wstaw/zaktualizuj timestamp
            conn.execute("""
                INSERT OR REPLACE INTO last_refresh (id, last_updated)
                VALUES (1, ?)
            """, (ts,))
            
            conn.commit()
    
    def _get_countries_from_db(self) -> List[Dict]:
        """Pobiera kraje z bazy danych"""
        try:
            with self._connect() as conn:
                cursor = conn.execute("""
                    SELECT id as country_id, name as country_name, currency_id
                    FROM countries WHERE is_available = 1
                """)
                return [dict(row) for row in cursor.fetchall()]
        except:
            return []
    
    def get_last_refresh_time(self) -> Optional[datetime]:
        """Zwraca czas ostatniej aktualizacji bazy danych"""
        try:
            with self._connect() as conn:
                cursor = conn.execute("SELECT last_updated FROM last_refresh WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    return datetime.fromisoformat(row['last_updated'].replace('Z', '+00:00'))
                return None
        except:
            return None
    
    def is_database_fresh(self, max_age_hours: int = 1) -> bool:
        """Sprawdza czy baza danych jest świeża (zaktualizowana w ostatnich X godzinach)"""
        last_refresh = self.get_last_refresh_time()
        if not last_refresh:
            return False
        
        age = datetime.now(last_refresh.tzinfo) - last_refresh
        return age < timedelta(hours=max_age_hours)
    
    # === METODY DO POBIERANIA DANYCH Z BAZY ===
    
    def get_countries_data(self) -> List[Dict]:
        """Pobiera dane krajów z bazy danych"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT id as country_id, name as country_name, 
                       currency_id, currency_name
                FROM countries WHERE is_available = 1
                ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_currencies_data(self) -> Dict[int, str]:
        """Pobiera mapę walut z bazy danych"""
        with self._connect() as conn:
            cursor = conn.execute("SELECT id, name FROM currencies")
            return {row['id']: row['name'] for row in cursor.fetchall()}
    
    def get_currency_rates(self) -> Dict[int, float]:
        """Pobiera najnowsze kursy walut z bazy danych"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT currency_id, rate_gold_per_unit
                FROM currency_rates 
                WHERE ts = (SELECT MAX(ts) FROM currency_rates)
            """)
            return {row['currency_id']: row['rate_gold_per_unit'] for row in cursor.fetchall()}
    
    def get_regions_data(self) -> Tuple[List[Dict], Dict]:
        """Pobiera najnowsze dane regionów z bazy danych"""
        with self._connect() as conn:
            # Pobierz dane regionów
            cursor = conn.execute("""
                SELECT region_name, country_name, country_id, pollution,
                       bonus_score, bonus_description, bonus_by_type,
                       population, nb_npcs, type, original_country_id, bonus_per_pollution
                FROM regions_data 
                WHERE created_at = (SELECT MAX(created_at) FROM regions_data)
                ORDER BY region_name
            """)
            
            regions_data = []
            for row in cursor.fetchall():
                region_dict = dict(row)
                # Parsuj JSON z bonus_by_type
                try:
                    region_dict['bonus_by_type'] = json.loads(region_dict['bonus_by_type'])
                except:
                    region_dict['bonus_by_type'] = {}
                regions_data.append(region_dict)
            
            # Pobierz podsumowanie regionów
            cursor = conn.execute("""
                SELECT summary_json
                FROM regions_summary 
                WHERE created_at = (SELECT MAX(created_at) FROM regions_summary)
            """)
            row = cursor.fetchone()
            summary = json.loads(row['summary_json']) if row else {}
            
            return regions_data, summary
    
    def get_job_offers(self) -> List[Dict]:
        """Pobiera najnowsze oferty pracy z bazy danych"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT country_id, country_name, wage_original, wage_gold,
                       currency_id, currency_name, job_title, business_name
                FROM job_offers 
                WHERE ts = (SELECT MAX(ts) FROM job_offers)
                ORDER BY wage_gold DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_market_offers(self) -> List[Dict]:
        """Pobiera najnowsze oferty rynkowe z bazy danych"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT item_id, item_name, country_id, country_name,
                       price_original, price_gold, currency_id, currency_name,
                       quantity, offer_type
                FROM market_offers 
                WHERE ts = (SELECT MAX(ts) FROM market_offers)
                ORDER BY price_gold ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_military_data(self) -> Tuple[List[Dict], Dict]:
        """Pobiera najnowsze dane militarne z bazy danych"""
        with self._connect() as conn:
            # Pobierz dane o walkach
            cursor = conn.execute("""
                SELECT hits_data_json
                FROM military_hits 
                WHERE ts = (SELECT MAX(ts) FROM military_hits)
            """)
            hits_row = cursor.fetchone()
            hits_data = json.loads(hits_row['hits_data_json']) if hits_row else []
            
            # Pobierz dane o wojnach
            cursor = conn.execute("""
                SELECT wars_summary_json
                FROM military_wars 
                WHERE ts = (SELECT MAX(ts) FROM military_wars)
            """)
            wars_row = cursor.fetchone()
            wars_summary = json.loads(wars_row['wars_summary_json']) if wars_row else {}
            
            return hits_data, wars_summary
    
    def get_warriors_data(self) -> List[Dict]:
        """Pobiera najnowsze dane wojowników z bazy danych"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT warriors_data_json
                FROM warriors_ranking 
                WHERE ts = (SELECT MAX(ts) FROM warriors_ranking)
            """)
            row = cursor.fetchone()
            return json.loads(row['warriors_data_json']) if row else []
