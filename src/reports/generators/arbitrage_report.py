#!/usr/bin/env python3
"""
Consolidated currency arbitrage analyzer for Eclesiar.
Combines the best features from both versions.
"""

from datetime import datetime, timedelta
import os
import sys
import time
import json
import csv
from typing import Any, Dict, List, Tuple, Optional, NamedTuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import statistics
import math

from config.settings.base import AUTH_TOKEN, GOLD_ID_FALLBACK, MIN_PROFIT_THRESHOLD, API_WORKERS_MARKET
from src.data.api.client import fetch_data
from src.core.services.economy_service import fetch_countries_and_currencies, build_currency_rates_map


@dataclass
class MarketOffer:
    """Represents an offer in the currency market"""
    rate: float
    amount: float
    owner_id: int
    transaction_type: str  # 'BUY' or 'SELL'
    timestamp: datetime


@dataclass
class CurrencyMarket:
    """Reprezentuje rynek dla konkretnej waluty"""
    currency_id: int
    currency_name: str
    currency_code: str
    buy_offers: List[MarketOffer]
    sell_offers: List[MarketOffer]
    best_buy_rate: float
    best_sell_rate: float
    spread: float
    volume_24h: float
    liquidity_score: float
    last_updated: datetime


@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    from_currency: str
    to_currency: str
    buy_rate: float
    sell_rate: float
    profit_percentage: float
    min_amount: float
    max_amount: float
    estimated_profit_gold: float
    risk_score: float
    timestamp: datetime


@dataclass
class PortfolioPosition:
    """Represents a portfolio position"""
    currency_name: str
    amount: float
    avg_buy_rate: float
    current_rate: float
    unrealized_pnl: float
    last_updated: datetime


@dataclass
class BacktestResult:
    """Reprezentuje wynik backtestingu"""
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percentage: float
    max_drawdown: float
    total_trades: int
    profitable_trades: int
    win_rate: float
    avg_profit_per_trade: float
    avg_loss_per_trade: float
    profit_factor: float


class RiskAnalyzer:
    """Analizator ryzyka dla transakcji arbitrażowych"""
    
    def __init__(self):
        self.risk_factors = {
            'spread_volatility': 0.3,
            'liquidity_risk': 0.25,
            'execution_risk': 0.2,
            'market_impact': 0.15,
            'counterparty_risk': 0.1
        }
    
    def calculate_risk_score(self, opportunity: ArbitrageOpportunity) -> float:
        """Calculates risk score for arbitrage opportunity"""
        try:
            risk_score = 0.0
            
            # Spread volatility risk
            if opportunity.profit_percentage < 1.0:
                risk_score += self.risk_factors['spread_volatility'] * 0.8
            elif opportunity.profit_percentage < 2.0:
                risk_score += self.risk_factors['spread_volatility'] * 0.4
            else:
                risk_score += self.risk_factors['spread_volatility'] * 0.1
            
            # Liquidity risk
            if opportunity.liquidity_score < 0.3:
                risk_score += self.risk_factors['liquidity_risk'] * 1.0
            elif opportunity.liquidity_score < 0.6:
                risk_score += self.risk_factors['liquidity_risk'] * 0.5
            else:
                risk_score += self.risk_factors['liquidity_risk'] * 0.1
            
            # Execution risk
            if opportunity.execution_time_estimate > 300:  # 5 minutes
                risk_score += self.risk_factors['execution_risk'] * 1.0
            elif opportunity.execution_time_estimate > 60:  # 1 minute
                risk_score += self.risk_factors['execution_risk'] * 0.5
            else:
                risk_score += self.risk_factors['execution_risk'] * 0.1
            
            # Market impact risk
            if opportunity.volume_score < 0.3:
                risk_score += self.risk_factors['market_impact'] * 1.0
            elif opportunity.volume_score < 0.6:
                risk_score += self.risk_factors['market_impact'] * 0.5
            else:
                risk_score += self.risk_factors['market_impact'] * 0.1
            
            # Counterparty risk (always present)
            risk_score += self.risk_factors['counterparty_risk']
            
            return min(1.0, risk_score)
            
        except Exception as e:
            print(f"Error calculating risk score: {e}")
            return 1.0  # Maximum risk on error


class CurrencyArbitrageAnalyzer:
    """Konsolidowany analizator arbitrażu walutowego"""
    
    def __init__(self, ticket_cost_gold: float = 0.1, min_profit_threshold: float = 0.5):
        """
        Inicjalizuje analizator arbitrażu walutowego.
        
        Args:
            ticket_cost_gold: Koszt biletu w złocie (domyślnie 0.1)
            min_profit_threshold: Minimalny próg zysku w procentach (domyślnie 0.5%)
        """
        self.ticket_cost_gold = ticket_cost_gold
        self.min_profit_threshold = min_profit_threshold
        self.eco_countries = {}
        self.currencies_map = {}
        self.currency_codes_map = {}
        self.gold_id = GOLD_ID_FALLBACK
        self.currency_rates = {}
        self.risk_analyzer = RiskAnalyzer()
        
    def fetch_market_data_for_currency(self, currency_id: int, currency_name: str) -> Optional[CurrencyMarket]:
        """
        Pobiera dane rynkowe dla konkretnej waluty.
        
        Args:
            currency_id: ID waluty
            currency_name: Nazwa waluty
            
        Returns:
            Obiekt CurrencyMarket lub None w przypadku błędu
        """
        try:
            # Pobierz oferty kupna
            buy_response = fetch_data(
                f"market/coin/get?currency_id={currency_id}&transaction=BUY",
                f"ofertach kupna dla {currency_name}"
            )
            
            # Pobierz oferty sprzedaży
            sell_response = fetch_data(
                f"market/coin/get?currency_id={currency_id}&transaction=SELL",
                f"ofertach sprzedaży dla {currency_name}"
            )
            
            if not buy_response or not sell_response:
                return None
                
            buy_offers = []
            sell_offers = []
            
            # Przetwórz oferty kupna
            if 'data' in buy_response:
                for offer in buy_response['data']:
                    buy_offers.append(MarketOffer(
                        rate=float(offer.get('rate', 0)),
                        amount=float(offer.get('amount', 0)),
                        owner_id=int(offer.get('owner_id', 0)),
                        transaction_type='BUY',
                        timestamp=datetime.now()
                    ))
            
            # Przetwórz oferty sprzedaży
            if 'data' in sell_response:
                for offer in sell_response['data']:
                    sell_offers.append(MarketOffer(
                        rate=float(offer.get('rate', 0)),
                        amount=float(offer.get('amount', 0)),
                        owner_id=int(offer.get('owner_id', 0)),
                        transaction_type='SELL',
                        timestamp=datetime.now()
                    ))
            
            if not buy_offers or not sell_offers:
                return None
            
            # Sortuj oferty
            buy_offers.sort(key=lambda x: x.rate, reverse=True)  # Najwyższe ceny kupna
            sell_offers.sort(key=lambda x: x.rate)  # Najniższe ceny sprzedaży
            
            best_buy_rate = buy_offers[0].rate if buy_offers else 0
            best_sell_rate = sell_offers[0].rate if sell_offers else 0
            spread = best_sell_rate - best_buy_rate if best_buy_rate > 0 and best_sell_rate > 0 else 0
            
            # Oblicz volume 24h
            volume_24h = sum(offer.amount for offer in buy_offers + sell_offers)
            
            # Oblicz volatility
            all_rates = [offer.rate for offer in buy_offers + sell_offers]
            volatility = statistics.stdev(all_rates) if len(all_rates) > 1 else 0
            
            # Oblicz liquidity score
            liquidity_score = min(1.0, len(buy_offers + sell_offers) / 100.0)
            
            return CurrencyMarket(
                currency_id=currency_id,
                currency_name=currency_name,
                currency_code=self.currency_codes_map.get(currency_id, str(currency_id)),
                buy_offers=buy_offers,
                sell_offers=sell_offers,
                best_buy_rate=best_buy_rate,
                best_sell_rate=best_sell_rate,
                spread=spread,
                volume_24h=volume_24h,
                liquidity_score=liquidity_score,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            print(f"Error fetching market data for {currency_name}: {e}")
            return None
    
    def find_arbitrage_opportunities(self, use_database: bool = True) -> List[ArbitrageOpportunity]:
        """Znajduje okazje do arbitrażu między wszystkimi walutami (DB-first approach)"""
        try:
            opportunities = []
            
            if use_database:
                # Spróbuj załadować dane z bazy danych
                try:
                    from src.core.services.database_manager_service import DatabaseManagerService
                    db_manager = DatabaseManagerService()
                    
                    # Pobierz dane z bazy
                    countries = db_manager.get_countries_data()
                    self.currencies_map = db_manager.get_currencies_data()
                    self.currency_rates = db_manager.get_currency_rates()
                    
                    # Konwertuj kraje do formatu oczekiwanego
                    self.eco_countries = [
                        {
                            'country_id': c['country_id'],
                            'country_name': c['country_name'],
                            'currency_id': c['currency_id']
                        }
                        for c in countries
                    ]
                    
                    # Znajdź GOLD ID
                    self.gold_id = GOLD_ID_FALLBACK
                    for curr_id, curr_name in self.currencies_map.items():
                        if curr_name.upper() == 'GOLD':
                            self.gold_id = curr_id
                            break
                    
                    print(f"✅ Loaded data from database: {len(self.currencies_map)} currencies, {len(self.currency_rates)} rates")
                    
                except Exception as e:
                    print(f"⚠️ Error loading from database: {e}")
                    print("🔄 Falling back to API...")
                    use_database = False
            
            if not use_database:
                # Fallback: Pobierz dane z API
                self.eco_countries, self.currencies_map, self.currency_codes_map, self.gold_id = fetch_countries_and_currencies()
                
                if not self.eco_countries or not self.currencies_map:
                    print("Error: Cannot fetch countries and currencies data")
                    return []
                
                # Pobierz kursy walut
                self.currency_rates = build_currency_rates_map(self.currencies_map, self.gold_id)
            
            # Pobierz dane rynkowe dla wszystkich walut
            currency_ids = list(self.currencies_map.keys())
            
            print(f"Analizowanie {len(currency_ids)} walut...")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_currency = {
                    executor.submit(self.fetch_market_data_for_currency, cid, self.currencies_map[cid]): cid 
                    for cid in currency_ids
                }
                
                markets = {}
                for future in as_completed(future_to_currency):
                    currency_id = future_to_currency[future]
                    try:
                        market = future.result()
                        if market:
                            markets[currency_id] = market
                    except Exception as e:
                        print(f"Error fetching data for currency {currency_id}: {e}")
            
            print(f"Fetched market data for {len(markets)} currencies")
            
            # Znajdź okazje arbitrażowe
            for from_currency_id, from_market in markets.items():
                for to_currency_id, to_market in markets.items():
                    if from_currency_id == to_currency_id:
                        continue
                    
                    # Sprawdź czy można kupić w jednej walucie i sprzedać w drugiej
                    if (from_market.best_buy_rate > 0 and to_market.best_sell_rate > 0 and
                        from_market.best_buy_rate < to_market.best_sell_rate):
                        
                        # Oblicz zysk
                        buy_rate = from_market.best_buy_rate
                        sell_rate = to_market.best_sell_rate
                        profit_percentage = ((sell_rate - buy_rate) / buy_rate) * 100
                        
                        if profit_percentage >= self.min_profit_threshold:
                            # Oblicz maksymalną kwotę
                            max_amount = min(
                                from_market.buy_offers[0].amount if from_market.buy_offers else 0,
                                to_market.sell_offers[0].amount if to_market.sell_offers else 0
                            )
                            
                            # Oblicz szacowany zysk w złocie
                            estimated_profit_gold = (sell_rate - buy_rate) * max_amount
                            
                            # Oblicz score'y
                            volume_score = min(1.0, max_amount / 1000.0)  # Normalizuj do 1000
                            liquidity_score = (from_market.liquidity_score + to_market.liquidity_score) / 2
                            
                            # Szacuj czas wykonania
                            execution_time_estimate = 60 + (len(from_market.buy_offers) + len(to_market.sell_offers)) * 10
                            
                            opportunity = ArbitrageOpportunity(
                                from_currency=from_market.currency_name,
                                to_currency=to_market.currency_name,
                                buy_rate=buy_rate,
                                sell_rate=sell_rate,
                                profit_percentage=profit_percentage,
                                min_amount=0.1,
                                max_amount=max_amount,
                                estimated_profit_gold=estimated_profit_gold,
                                risk_score=0.0,  # Zostanie obliczone później
                                timestamp=datetime.now()
                            )
                            
                            # Oblicz score ryzyka
                            opportunity.risk_score = self.risk_analyzer.calculate_risk_score(opportunity)
                            
                            opportunities.append(opportunity)
            
            # Sortuj według zysku
            opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
            
            return opportunities
            
        except Exception as e:
            print(f"Error searching for arbitrage opportunities: {e}")
            return []
    
    def generate_arbitrage_report(self, opportunities: List[ArbitrageOpportunity], 
                                 output_format: str = "txt") -> str:
        """Generuje raport arbitrażowy"""
        try:
            if not opportunities:
                return "Brak okazji arbitrażowych spełniających kryteria."
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if output_format.lower() == "csv":
                filename = f"arbitrage_report_{timestamp}.csv"
                self._save_csv_report(opportunities, filename)
                return f"Raport CSV zapisany jako: {filename}"
            else:
                filename = f"arbitrage_report_{timestamp}.txt"
                self._save_txt_report(opportunities, filename)
                return f"Raport TXT zapisany jako: {filename}"
                
        except Exception as e:
            return f"Błąd podczas generowania raportu: {e}"
    
    def _save_csv_report(self, opportunities: List[ArbitrageOpportunity], filename: str):
        """Zapisuje raport w formacie CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'from_currency', 'to_currency', 'buy_rate', 'sell_rate', 
                    'profit_percentage', 'max_amount', 'estimated_profit_gold',
                    'risk_score', 'volume_score', 'liquidity_score', 'execution_time_estimate'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for opp in opportunities:
                    writer.writerow({
                        'from_currency': opp.from_currency,
                        'to_currency': opp.to_currency,
                        'buy_rate': f"{opp.buy_rate:.6f}",
                        'sell_rate': f"{opp.sell_rate:.6f}",
                        'profit_percentage': f"{opp.profit_percentage:.2f}",
                        'max_amount': f"{opp.max_amount:.2f}",
                        'estimated_profit_gold': f"{opp.estimated_profit_gold:.6f}",
                        'risk_score': f"{opp.risk_score:.3f}",
                        'volume_score': f"{opp.volume_score:.3f}",
                        'liquidity_score': f"{opp.liquidity_score:.3f}",
                        'execution_time_estimate': f"{opp.execution_time_estimate:.0f}"
                    })
                    
        except Exception as e:
            print(f"Error saving CSV report: {e}")
    
    def _save_txt_report(self, opportunities: List[ArbitrageOpportunity], filename: str):
        """Zapisuje raport w formacie TXT"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== RAPORT ARBITRAŻU WALUTOWEGO ===\n")
                f.write(f"Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Liczba znalezionych okazji: {len(opportunities)}\n")
                f.write(f"Minimalny próg zysku: {self.min_profit_threshold}%\n")
                f.write("=" * 50 + "\n\n")
                
                for i, opp in enumerate(opportunities, 1):
                    f.write(f"{i:2d}. {opp.from_currency} → {opp.to_currency}\n")
                    f.write(f"    Kupno: {opp.buy_rate:.6f} | Sprzedaż: {opp.sell_rate:.6f}\n")
                    f.write(f"    Zysk: {opp.profit_percentage:.2f}% | Maks. kwota: {opp.max_amount:.2f}\n")
                    f.write(f"    Szacowany zysk: {opp.estimated_profit_gold:.6f} GOLD\n")
                    f.write(f"    Ryzyko: {opp.risk_score:.3f} | Płynność: {opp.liquidity_score:.3f}\n")
                    f.write(f"    Czas wykonania: {opp.execution_time_estimate:.0f}s\n")
                    f.write("-" * 40 + "\n")
                    
        except Exception as e:
            print(f"Error saving TXT report: {e}")


def main():
    """Główna funkcja do testowania"""
    analyzer = CurrencyArbitrageAnalyzer(min_profit_threshold=0.5)
    
    print("🔍 Searching for arbitrage opportunities...")
    opportunities = analyzer.find_arbitrage_opportunities()
    
    if opportunities:
        print(f"✅ Found {len(opportunities)} arbitrage opportunities")
        
        # Generuj raporty
        csv_result = analyzer.generate_arbitrage_report(opportunities, "csv")
        txt_result = analyzer.generate_arbitrage_report(opportunities, "txt")
        
        print(f"📊 {csv_result}")
        print(f"📄 {txt_result}")
        
        # Pokaż top 5 okazji
        print("\n🏆 TOP 5 ARBITRAGE OPPORTUNITIES:")
        print("-" * 60)
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp.from_currency} → {opp.to_currency}")
            print(f"   Zysk: {opp.profit_percentage:.2f}% | Ryzyko: {opp.risk_score:.3f}")
            print(f"   Szacowany zysk: {opp.estimated_profit_gold:.6f} GOLD")
            print()
    else:
        print("❌ No arbitrage opportunities found meeting the criteria.")


if __name__ == "__main__":
    main()
