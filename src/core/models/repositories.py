"""
Repository interfaces for the Eclesiar application.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .entities import (
    Country, Currency, Region, Item, MarketOffer, 
    CurrencyMarket, ProductionData, ArbitrageOpportunity, ReportData
)


class BaseRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    def save(self, entity: Any) -> bool:
        """Save entity to storage"""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[Any]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Any]:
        """Find all entities"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID"""
        pass


class CountryRepository(BaseRepository):
    """Repository for Country entities"""
    
    @abstractmethod
    def find_by_currency_id(self, currency_id: int) -> List[Country]:
        """Find countries by currency ID"""
        pass
    
    @abstractmethod
    def find_available_countries(self) -> List[Country]:
        """Find all available countries"""
        pass


class CurrencyRepository(BaseRepository):
    """Repository for Currency entities"""
    
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Currency]:
        """Find currency by code"""
        pass
    
    @abstractmethod
    def find_gold_currency(self) -> Optional[Currency]:
        """Find GOLD currency"""
        pass
    
    @abstractmethod
    def get_currency_rates(self, currency_id: int) -> List[Tuple[datetime, float]]:
        """Get currency rate history"""
        pass


class RegionRepository(BaseRepository):
    """Repository for Region entities"""
    
    @abstractmethod
    def find_by_country_id(self, country_id: int) -> List[Region]:
        """Find regions by country ID"""
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Region]:
        """Find region by name"""
        pass
    
    @abstractmethod
    def find_best_for_production(self, item_name: str, limit: int = 10) -> List[Region]:
        """Find best regions for production of specific item"""
        pass


class ItemRepository(BaseRepository):
    """Repository for Item entities"""
    
    @abstractmethod
    def find_by_type(self, item_type: str) -> List[Item]:
        """Find items by type"""
        pass
    
    @abstractmethod
    def find_cheapest_by_type(self, item_type: str) -> Optional[Item]:
        """Find cheapest item by type"""
        pass
    
    @abstractmethod
    def get_price_history(self, item_id: int) -> List[Tuple[datetime, float]]:
        """Get item price history"""
        pass


class MarketRepository(BaseRepository):
    """Repository for Market entities"""
    
    @abstractmethod
    def get_currency_market(self, currency_id: int) -> Optional[CurrencyMarket]:
        """Get currency market data"""
        pass
    
    @abstractmethod
    def find_arbitrage_opportunities(self, min_profit: float = 0.5) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities"""
        pass
    
    @abstractmethod
    def save_market_offers(self, offers: List[MarketOffer]) -> bool:
        """Save market offers"""
        pass


class ProductionRepository(BaseRepository):
    """Repository for Production entities"""
    
    @abstractmethod
    def get_production_data(self, region_id: int, item_name: str) -> Optional[ProductionData]:
        """Get production data for region and item"""
        pass
    
    @abstractmethod
    def get_best_production_regions(self, item_name: str, limit: int = 10) -> List[ProductionData]:
        """Get best production regions for item"""
        pass
    
    @abstractmethod
    def save_production_analysis(self, data: List[ProductionData]) -> bool:
        """Save production analysis data"""
        pass


class ReportRepository(BaseRepository):
    """Repository for Report entities"""
    
    @abstractmethod
    def save_report(self, report: ReportData) -> bool:
        """Save report data"""
        pass
    
    @abstractmethod
    def get_report_history(self, report_type: str, limit: int = 10) -> List[ReportData]:
        """Get report history"""
        pass
    
    @abstractmethod
    def get_latest_report(self, report_type: str) -> Optional[ReportData]:
        """Get latest report of specific type"""
        pass
