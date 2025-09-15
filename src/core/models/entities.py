"""
Domain entities for the Eclesiar application.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class TransactionType(Enum):
    """Transaction types for currency market"""
    BUY = "BUY"
    SELL = "SELL"


class ReportType(Enum):
    """Report types"""
    DAILY = "daily"
    PRODUCTION = "production"
    ARBITRAGE = "arbitrage"
    SHORT_ECONOMIC = "short_economic"
    HTML = "html"
    GOOGLE_SHEETS = "google_sheets"


@dataclass
class Country:
    """Country entity"""
    id: int
    name: str
    currency_id: int
    currency_name: str
    is_available: bool = True


@dataclass
class Currency:
    """Currency entity"""
    id: int
    name: str
    code: str
    rate_gold_per_unit: Optional[float] = None


@dataclass
class Region:
    """Region entity"""
    id: int
    name: str
    country_id: int
    country_name: str
    pollution: float
    bonus_score: float
    bonus_description: str
    bonus_by_type: Dict[str, Any]
    population: int
    nb_npcs: int
    type: str
    original_country_id: int
    bonus_per_pollution: float


@dataclass
class Item:
    """Item entity"""
    id: int
    name: str
    type: str
    price_gold: Optional[float] = None
    country_id: Optional[int] = None
    currency_id: Optional[int] = None


@dataclass
class MarketOffer:
    """Market offer entity"""
    rate: float
    amount: float
    owner_id: int
    transaction_type: TransactionType
    timestamp: datetime


@dataclass
class CurrencyMarket:
    """Currency market entity"""
    currency_id: int
    currency_name: str
    buy_offers: List[MarketOffer]
    sell_offers: List[MarketOffer]
    best_buy_rate: Optional[float] = None
    best_sell_rate: Optional[float] = None


@dataclass
class ProductionData:
    """Production data entity"""
    region_name: str
    country_name: str
    country_id: int
    item_name: str
    total_bonus: float
    regional_bonus: float
    country_bonus: float
    bonus_type: str
    pollution: float
    npc_wages: float
    production_q1: int
    production_q2: int
    production_q3: int
    production_q4: int
    production_q5: int
    efficiency_score: float


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity entity"""
    currency_id: int
    currency_name: str
    buy_country: str
    sell_country: str
    buy_rate: float
    sell_rate: float
    profit_percentage: float
    profit_gold: float
    risk_score: float
    liquidity_score: float


@dataclass
class ReportData:
    """Report data entity"""
    report_type: ReportType
    sections: Dict[str, bool]
    data: Dict[str, Any]
    generated_at: datetime
    output_path: Optional[str] = None
