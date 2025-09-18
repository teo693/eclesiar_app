"""
SQLite implementation of repositories.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from src.core.models.entities import (
    Country, Currency, Region, Item, MarketOffer, 
    CurrencyMarket, ProductionData, ArbitrageOpportunity, ReportData,
    TransactionType, ReportType
)
from src.core.models.repositories import (
    CountryRepository, CurrencyRepository, RegionRepository,
    ItemRepository, MarketRepository, ProductionRepository, ReportRepository
)


class SQLiteRepositoryMixin:
    """Mixin for SQLite database operations"""
    
    def __init__(self, db_path: str = "data/eclesiar.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _connect(self) -> sqlite3.Connection:
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn
    
    def _execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute query and return results"""
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def _execute_update(self, query: str, params: Tuple = ()) -> bool:
        """Execute update query"""
        try:
            with self._connect() as conn:
                conn.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            print(f"Database error: {e}")
            return False


class SQLiteCountryRepository(SQLiteRepositoryMixin, CountryRepository):
    """SQLite implementation of CountryRepository"""
    
    def save(self, entity: Country) -> bool:
        query = """
        INSERT OR REPLACE INTO countries 
        (id, name, currency_id, currency_name, is_available)
        VALUES (?, ?, ?, ?, ?)
        """
        return self._execute_update(query, (
            entity.id, entity.name, entity.currency_id, 
            entity.currency_name, entity.is_available
        ))
    
    def find_by_id(self, entity_id: int) -> Optional[Country]:
        query = "SELECT * FROM countries WHERE id = ?"
        rows = self._execute_query(query, (entity_id,))
        if rows:
            row = rows[0]
            return Country(
                id=row['id'],
                name=row['name'],
                currency_id=row['currency_id'],
                currency_name=row['currency_name'],
                is_available=bool(row['is_available'])
            )
        return None
    
    def find_all(self) -> List[Country]:
        query = "SELECT * FROM countries"
        rows = self._execute_query(query)
        return [
            Country(
                id=row['id'],
                name=row['name'],
                currency_id=row['currency_id'],
                currency_name=row['currency_name'],
                is_available=bool(row['is_available'])
            )
            for row in rows
        ]
    
    def delete(self, entity_id: int) -> bool:
        query = "DELETE FROM countries WHERE id = ?"
        return self._execute_update(query, (entity_id,))
    
    def find_by_currency_id(self, currency_id: int) -> List[Country]:
        query = "SELECT * FROM countries WHERE currency_id = ?"
        rows = self._execute_query(query, (currency_id,))
        return [
            Country(
                id=row['id'],
                name=row['name'],
                currency_id=row['currency_id'],
                currency_name=row['currency_name'],
                is_available=bool(row['is_available'])
            )
            for row in rows
        ]
    
    def find_available_countries(self) -> List[Country]:
        query = "SELECT * FROM countries WHERE is_available = 1"
        rows = self._execute_query(query)
        return [
            Country(
                id=row['id'],
                name=row['name'],
                currency_id=row['currency_id'],
                currency_name=row['currency_name'],
                is_available=bool(row['is_available'])
            )
            for row in rows
        ]


class SQLiteCurrencyRepository(SQLiteRepositoryMixin, CurrencyRepository):
    """SQLite implementation of CurrencyRepository"""
    
    def save(self, entity: Currency) -> bool:
        query = """
        INSERT OR REPLACE INTO currencies 
        (id, name, code, rate_gold_per_unit)
        VALUES (?, ?, ?, ?)
        """
        return self._execute_update(query, (
            entity.id, entity.name, entity.code, entity.rate_gold_per_unit
        ))
    
    def find_by_id(self, entity_id: int) -> Optional[Currency]:
        query = "SELECT * FROM currencies WHERE id = ?"
        rows = self._execute_query(query, (entity_id,))
        if rows:
            row = rows[0]
            return Currency(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                rate_gold_per_unit=row['rate_gold_per_unit']
            )
        return None
    
    def find_all(self) -> List[Currency]:
        query = "SELECT * FROM currencies"
        rows = self._execute_query(query)
        return [
            Currency(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                rate_gold_per_unit=row['rate_gold_per_unit']
            )
            for row in rows
        ]
    
    def delete(self, entity_id: int) -> bool:
        query = "DELETE FROM currencies WHERE id = ?"
        return self._execute_update(query, (entity_id,))
    
    def find_by_code(self, code: str) -> Optional[Currency]:
        query = "SELECT * FROM currencies WHERE code = ?"
        rows = self._execute_query(query, (code,))
        if rows:
            row = rows[0]
            return Currency(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                rate_gold_per_unit=row['rate_gold_per_unit']
            )
        return None
    
    def find_gold_currency(self) -> Optional[Currency]:
        query = "SELECT * FROM currencies WHERE code = 'GOLD' OR name LIKE '%GOLD%'"
        rows = self._execute_query(query)
        if rows:
            row = rows[0]
            return Currency(
                id=row['id'],
                name=row['name'],
                code=row['code'],
                rate_gold_per_unit=row['rate_gold_per_unit']
            )
        return None
    
    def get_currency_rates(self, currency_id: int) -> List[Tuple[datetime, float]]:
        query = """
        SELECT ts, rate_gold_per_unit 
        FROM currency_rates 
        WHERE currency_id = ? 
        ORDER BY ts DESC
        """
        rows = self._execute_query(query, (currency_id,))
        return [
            (datetime.fromisoformat(row['ts'].replace('Z', '+00:00')), row['rate_gold_per_unit'])
            for row in rows
        ]


class SQLiteRegionRepository(SQLiteRepositoryMixin, RegionRepository):
    """SQLite implementation of RegionRepository"""
    
    def save(self, entity: Region) -> bool:
        query = """
        INSERT OR REPLACE INTO regions 
        (id, name, country_id, country_name, pollution, bonus_score, 
         bonus_description, bonus_by_type, population, nb_npcs, type, 
         original_country_id, bonus_per_pollution)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self._execute_update(query, (
            entity.id, entity.name, entity.country_id, entity.country_name,
            entity.pollution, entity.bonus_score, entity.bonus_description,
            json.dumps(entity.bonus_by_type), entity.population, entity.nb_npcs,
            entity.type, entity.original_country_id, entity.bonus_per_pollution
        ))
    
    def find_by_id(self, entity_id: int) -> Optional[Region]:
        query = "SELECT * FROM regions WHERE id = ?"
        rows = self._execute_query(query, (entity_id,))
        if rows:
            row = rows[0]
            return Region(
                id=row['id'],
                name=row['name'],
                country_id=row['country_id'],
                country_name=row['country_name'],
                pollution=row['pollution'],
                bonus_score=row['bonus_score'],
                bonus_description=row['bonus_description'],
                bonus_by_type=json.loads(row['bonus_by_type']) if row['bonus_by_type'] else {},
                population=row['population'],
                nb_npcs=row['nb_npcs'],
                type=row['type'],
                original_country_id=row['original_country_id'],
                bonus_per_pollution=row['bonus_per_pollution']
            )
        return None
    
    def find_all(self) -> List[Region]:
        query = "SELECT * FROM regions"
        rows = self._execute_query(query)
        return [
            Region(
                id=row['id'],
                name=row['name'],
                country_id=row['country_id'],
                country_name=row['country_name'],
                pollution=row['pollution'],
                bonus_score=row['bonus_score'],
                bonus_description=row['bonus_description'],
                bonus_by_type=json.loads(row['bonus_by_type']) if row['bonus_by_type'] else {},
                population=row['population'],
                nb_npcs=row['nb_npcs'],
                type=row['type'],
                original_country_id=row['original_country_id'],
                bonus_per_pollution=row['bonus_per_pollution']
            )
            for row in rows
        ]
    
    def delete(self, entity_id: int) -> bool:
        query = "DELETE FROM regions WHERE id = ?"
        return self._execute_update(query, (entity_id,))
    
    def find_by_country_id(self, country_id: int) -> List[Region]:
        query = "SELECT * FROM regions WHERE country_id = ?"
        rows = self._execute_query(query, (country_id,))
        return [
            Region(
                id=row['id'],
                name=row['name'],
                country_id=row['country_id'],
                country_name=row['country_name'],
                pollution=row['pollution'],
                bonus_score=row['bonus_score'],
                bonus_description=row['bonus_description'],
                bonus_by_type=json.loads(row['bonus_by_type']) if row['bonus_by_type'] else {},
                population=row['population'],
                nb_npcs=row['nb_npcs'],
                type=row['type'],
                original_country_id=row['original_country_id'],
                bonus_per_pollution=row['bonus_per_pollution']
            )
            for row in rows
        ]
    
    def find_by_name(self, name: str) -> Optional[Region]:
        query = "SELECT * FROM regions WHERE name = ?"
        rows = self._execute_query(query, (name,))
        if rows:
            row = rows[0]
            return Region(
                id=row['id'],
                name=row['name'],
                country_id=row['country_id'],
                country_name=row['country_name'],
                pollution=row['pollution'],
                bonus_score=row['bonus_score'],
                bonus_description=row['bonus_description'],
                bonus_by_type=json.loads(row['bonus_by_type']) if row['bonus_by_type'] else {},
                population=row['population'],
                nb_npcs=row['nb_npcs'],
                type=row['type'],
                original_country_id=row['original_country_id'],
                bonus_per_pollution=row['bonus_per_pollution']
            )
        return None
    
    def find_best_for_production(self, item_name: str, limit: int = 10) -> List[Region]:
        # This would need to be implemented based on production data
        # For now, return regions ordered by bonus score
        query = """
        SELECT * FROM regions 
        ORDER BY bonus_score DESC 
        LIMIT ?
        """
        rows = self._execute_query(query, (limit,))
        return [
            Region(
                id=row['id'],
                name=row['name'],
                country_id=row['country_id'],
                country_name=row['country_name'],
                pollution=row['pollution'],
                bonus_score=row['bonus_score'],
                bonus_description=row['bonus_description'],
                bonus_by_type=json.loads(row['bonus_by_type']) if row['bonus_by_type'] else {},
                population=row['population'],
                nb_npcs=row['nb_npcs'],
                type=row['type'],
                original_country_id=row['original_country_id'],
                bonus_per_pollution=row['bonus_per_pollution']
            )
            for row in rows
        ]
