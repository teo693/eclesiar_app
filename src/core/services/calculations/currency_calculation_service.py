"""
Currency Calculation Service

Centralny serwis do wszystkich obliczeń związanych z walutami.
Eliminuje duplikację logiki obliczeniowej kursów walut w całej aplikacji.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from src.data.api.client import fetch_data
from src.core.models.entities import ArbitrageOpportunity


@dataclass
class CurrencyRateInfo:
    """Informacje o kursie waluty"""
    currency_id: int
    currency_name: str
    rate_to_gold: float
    last_updated: datetime
    source: str  # 'api' or 'cache'


@dataclass
class CurrencyExtremes:
    """Informacje o ekstremach walutowych"""
    highest: Tuple[int, float, str]  # (id, rate, name)
    lowest: Tuple[int, float, str]   # (id, rate, name)


class CurrencyCalculationService:
    """Centralny serwis do wszystkich obliczeń związanych z walutami"""
    
    def __init__(self, cache_timeout_minutes: int = 15):
        self._currency_rates_cache: Dict[int, CurrencyRateInfo] = {}
        self._cache_timeout = timedelta(minutes=cache_timeout_minutes)
        self._gold_id: Optional[int] = None
        
    def get_currency_to_gold_rate(self, currency_id: int, use_cache: bool = True) -> Optional[float]:
        """
        Pobiera kurs waluty względem GOLD z cache lub API.
        
        Args:
            currency_id: ID waluty
            use_cache: Czy używać cache (domyślnie True)
            
        Returns:
            Kurs waluty względem GOLD lub None jeśli nie udało się pobrać
        """
        # Sprawdź cache jeśli włączony
        if use_cache and currency_id in self._currency_rates_cache:
            cached_info = self._currency_rates_cache[currency_id]
            if datetime.now() - cached_info.last_updated < self._cache_timeout:
                return cached_info.rate_to_gold
        
        # Pobierz z API
        rate = self._fetch_currency_to_gold_rate_from_api(currency_id)
        
        # Zapisz w cache jeśli udało się pobrać
        if rate is not None:
            self._currency_rates_cache[currency_id] = CurrencyRateInfo(
                currency_id=currency_id,
                currency_name="Unknown",  # Będzie uzupełnione przez build_currency_rates_map
                rate_to_gold=rate,
                last_updated=datetime.now(),
                source='api'
            )
        
        return rate
    
    def _fetch_currency_to_gold_rate_from_api(self, currency_id: int) -> Optional[float]:
        """
        Pobiera najlepszą ofertę SELL dla waluty z API.
        Zwraca najniższy dostępny kurs (pierwsza oferta).
        """
        try:
            # Pobierz oferty SELL (sprzedaż waluty za GOLD)
            sell_res = fetch_data(
                f"market/coin/get?currency_id={currency_id}&transaction=SELL", 
                f"currency rates {currency_id}"
            )
            
            if not sell_res or sell_res.get("code") != 200:
                return None
                
            offers = sell_res.get("data", [])
            if not offers:
                return None
            
            # Zbierz wszystkie kursy
            rates = []
            for offer in offers:
                rate = offer.get("rate")
                if rate is not None:
                    try:
                        rate_f = float(rate)
                        if rate_f > 0:
                            rates.append(rate_f)
                    except (ValueError, TypeError):
                        continue
            
            if not rates:
                return None
            
            # Sortuj kursy rosnąco i zwróć pierwszy (najniższy)
            rates.sort()
            return rates[0]
                    
        except Exception as e:
            print(f"Error fetching currency rate for {currency_id}: {e}")
        
        return None
    
    def build_currency_rates_map(self, currencies: Dict[int, str], gold_id: int) -> Dict[int, float]:
        """
        Buduje kompletną mapę kursów wszystkich walut względem GOLD.
        
        Args:
            currencies: Słownik mapujący ID walut na nazwy
            gold_id: ID waluty GOLD
            
        Returns:
            Słownik mapujący ID walut na kursy względem GOLD
        """
        rates_map = {}
        self._gold_id = gold_id
        
        # GOLD zawsze ma kurs 1.0
        if gold_id is not None:
            rates_map[gold_id] = 1.0
            # Aktualizuj cache
            self._currency_rates_cache[gold_id] = CurrencyRateInfo(
                currency_id=gold_id,
                currency_name=currencies.get(gold_id, "GOLD"),
                rate_to_gold=1.0,
                last_updated=datetime.now(),
                source='fixed'
            )
        
        # Pobierz kursy dla pozostałych walut
        for currency_id, currency_name in currencies.items():
            if currency_id == gold_id:
                continue
            
            rate = self.get_currency_to_gold_rate(currency_id)
            if rate is not None and rate > 0:
                rates_map[currency_id] = rate
                # Aktualizuj nazwę w cache
                if currency_id in self._currency_rates_cache:
                    self._currency_rates_cache[currency_id].currency_name = currency_name
        
        return rates_map
    
    def convert_to_gold(self, amount: float, currency_id: int) -> Optional[float]:
        """
        Przelicza kwotę z dowolnej waluty na GOLD.
        
        Args:
            amount: Kwota w walucie źródłowej
            currency_id: ID waluty źródłowej
            
        Returns:
            Kwota w GOLD lub None jeśli nie udało się przeliczyć
        """
        if currency_id == self._gold_id:
            return amount
        
        rate = self.get_currency_to_gold_rate(currency_id)
        if rate is None or rate <= 0:
            return None
        
        return amount * rate
    
    def find_arbitrage_opportunities(self, 
                                   currencies_map: Dict[int, str], 
                                   min_profit: float = 0.1,
                                   max_opportunities: int = 10) -> List[ArbitrageOpportunity]:
        """
        Znajduje okazje arbitrażowe między walutami.
        
        Args:
            currencies_map: Mapa walut
            min_profit: Minimalny zysk procentowy
            max_opportunities: Maksymalna liczba okazji do zwrócenia
            
        Returns:
            Lista okazji arbitrażowych posortowana według zysku
        """
        opportunities = []
        
        try:
            for currency_id, currency_name in currencies_map.items():
                if currency_id == self._gold_id:
                    continue
                
                # Pobierz oferty BUY i SELL
                buy_offers = self._get_market_offers(currency_id, "BUY")
                sell_offers = self._get_market_offers(currency_id, "SELL")
                
                if not buy_offers or not sell_offers:
                    continue
                
                # Znajdź najlepsze kursy
                best_buy_rate = max(offer.get("rate", 0) for offer in buy_offers)
                best_sell_rate = min(offer.get("rate", float('inf')) for offer in sell_offers)
                
                if best_buy_rate > 0 and best_sell_rate < float('inf'):
                    # Oblicz zysk procentowy
                    profit_percent = ((best_buy_rate - best_sell_rate) / best_sell_rate) * 100
                    
                    if profit_percent >= min_profit:
                        opportunity = ArbitrageOpportunity(
                            currency_id=currency_id,
                            currency_name=currency_name,
                            buy_rate=best_buy_rate,
                            sell_rate=best_sell_rate,
                            profit_percent=profit_percent,
                            potential_volume=min(
                                sum(offer.get("amount", 0) for offer in buy_offers[:3]),
                                sum(offer.get("amount", 0) for offer in sell_offers[:3])
                            )
                        )
                        opportunities.append(opportunity)
        
        except Exception as e:
            print(f"Error finding arbitrage opportunities: {e}")
        
        # Sortuj według zysku i ogranicz liczbę
        opportunities.sort(key=lambda x: x.profit_percent, reverse=True)
        return opportunities[:max_opportunities]
    
    def _get_market_offers(self, currency_id: int, transaction_type: str) -> List[Dict[str, Any]]:
        """Pobiera oferty rynkowe dla waluty"""
        try:
            response = fetch_data(
                f"market/coin/get?currency_id={currency_id}&transaction={transaction_type}",
                f"market offers {currency_id} {transaction_type}"
            )
            
            if response and response.get("code") == 200:
                return response.get("data", [])
        except Exception as e:
            print(f"Error fetching market offers for {currency_id}: {e}")
        
        return []
    
    def get_currency_extremes(self, currencies_map: Dict[int, str]) -> CurrencyExtremes:
        """
        Zwraca najwyższą i najniższą wartość waluty względem GOLD.
        
        Args:
            currencies_map: Mapa walut
            
        Returns:
            Obiekty z informacjami o ekstremach
        """
        rates = []
        
        for currency_id, currency_name in currencies_map.items():
            if currency_id == self._gold_id:
                continue
            
            rate = self.get_currency_to_gold_rate(currency_id)
            if rate is not None and rate > 0:
                rates.append((currency_id, rate, currency_name))
        
        if not rates:
            return CurrencyExtremes(
                highest=(0, 0.0, "N/A"),
                lowest=(0, 0.0, "N/A")
            )
        
        # Sortuj według kursów
        rates.sort(key=lambda x: x[1])
        
        return CurrencyExtremes(
            highest=rates[-1],  # Najwyższy kurs
            lowest=rates[0]     # Najniższy kurs
        )
    
    def clear_cache(self):
        """Czyści cache kursów walut"""
        self._currency_rates_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Zwraca informacje o stanie cache"""
        return {
            "cached_currencies": len(self._currency_rates_cache),
            "cache_timeout_minutes": self._cache_timeout.total_seconds() / 60,
            "oldest_entry": min(
                (info.last_updated for info in self._currency_rates_cache.values()),
                default=None
            ),
            "newest_entry": max(
                (info.last_updated for info in self._currency_rates_cache.values()),
                default=None
            )
        }
