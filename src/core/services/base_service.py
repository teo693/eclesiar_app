"""
Base service class with dependency injection.
"""

from abc import ABC
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from src.core.models.repositories import (
    CountryRepository, CurrencyRepository, RegionRepository,
    ItemRepository, MarketRepository, ProductionRepository, ReportRepository
)


@dataclass
class ServiceDependencies:
    """Container for service dependencies"""
    country_repo: CountryRepository
    currency_repo: CurrencyRepository
    region_repo: RegionRepository
    item_repo: ItemRepository
    market_repo: MarketRepository
    production_repo: ProductionRepository
    report_repo: ReportRepository


class BaseService(ABC):
    """Base service class with dependency injection"""
    
    def __init__(self, dependencies: ServiceDependencies):
        self.deps = dependencies
        self._country_repo = dependencies.country_repo
        self._currency_repo = dependencies.currency_repo
        self._region_repo = dependencies.region_repo
        self._item_repo = dependencies.item_repo
        self._market_repo = dependencies.market_repo
        self._production_repo = dependencies.production_repo
        self._report_repo = dependencies.report_repo
    
    @property
    def country_repo(self) -> CountryRepository:
        return self._country_repo
    
    @property
    def currency_repo(self) -> CurrencyRepository:
        return self._currency_repo
    
    @property
    def region_repo(self) -> RegionRepository:
        return self._region_repo
    
    @property
    def item_repo(self) -> ItemRepository:
        return self._item_repo
    
    @property
    def market_repo(self) -> MarketRepository:
        return self._market_repo
    
    @property
    def production_repo(self) -> ProductionRepository:
        return self._production_repo
    
    @property
    def report_repo(self) -> ReportRepository:
        return self._report_repo
