"""
Market Calculation Service

Centralny serwis do obliczeń rynkowych (najlepsze oferty, arbitraż).
Implementuje logikę znajdowania najlepszych cen i okazji arbitrażowych.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from src.data.api.client import fetch_data
from src.core.models.entities import ArbitrageOpportunity


@dataclass
class MarketOffer:
    """Reprezentuje ofertę na rynku"""
    item_id: int
    item_name: str
    country_id: int
    country_name: str
    currency_id: int
    price_local: float
    price_gold: float
    amount: int
    transaction_type: str  # 'BUY' lub 'SELL'
    
    
@dataclass
class CheapestItemInfo:
    """Informacje o najtańszym towarze"""
    item_id: int
    item_name: str
    min_price_gold: float
    avg_price_gold: float
    best_country: str
    best_currency: str
    amount_available: int
    price_history: List[float]


@dataclass
class JobOffer:
    """Reprezentuje ofertę pracy"""
    country_id: int
    country_name: str
    currency_id: int
    currency_name: str
    business_id: int
    salary_local: float
    salary_gold: float
    amount: int
    economic_skill: int
    job_title: str  # Prawidłowo sformatowany tytuł


@dataclass
class MarketAnalysis:
    """Analiza rynku dla konkretnego towaru"""
    item_name: str
    total_offers: int
    cheapest_price: float
    most_expensive_price: float
    average_price: float
    median_price: float
    best_countries: List[Tuple[str, float]]  # (country, price)
    market_depth: int  # Total amount available
    price_volatility: float


class MarketCalculationService:
    """Centralny serwis do obliczeń rynkowych"""
    
    def __init__(self):
        self._market_cache: Dict[str, Any] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
    
    def find_cheapest_items_globally(self, 
                                   countries: Dict[int, Dict[str, Any]],
                                   items: Dict[int, str],
                                   currency_rates: Dict[int, float],
                                   gold_id: int,
                                   max_items: int = 50) -> Dict[int, CheapestItemInfo]:
        """
        Znajduje najtańsze oferty dla wszystkich towarów we wszystkich krajach.
        
        Args:
            countries: Słownik krajów
            items: Słownik towarów
            currency_rates: Kursy walut względem GOLD
            gold_id: ID waluty GOLD
            max_items: Maksymalna liczba towarów do sprawdzenia
            
        Returns:
            Słownik mapujący ID towaru na informacje o najtańszej ofercie
        """
        cheapest_items = {}
        
        items_to_check = list(items.items())[:max_items]
        
        for item_id, item_name in items_to_check:
            try:
                best_offers = []
                
                for country_id, country_info in countries.items():
                    # Pobierz oferty dla towaru w tym kraju
                    offers = self._get_item_offers_in_country(item_id, country_id)
                    
                    if not offers:
                        continue
                    
                    # Przelicz ceny na GOLD
                    currency_id = country_info.get("currency_id")
                    if currency_id == gold_id:
                        rate = 1.0
                    else:
                        rate = currency_rates.get(currency_id)
                    
                    if not rate or rate <= 0:
                        continue
                    
                    # Przetwórz oferty
                    for offer in offers:
                        try:
                            price_local = float(offer.get("value", 0))
                            amount = int(offer.get("amount", 0))
                            
                            if price_local > 0 and amount > 0:
                                price_gold = price_local * rate
                                
                                market_offer = MarketOffer(
                                    item_id=item_id,
                                    item_name=item_name,
                                    country_id=country_id,
                                    country_name=country_info.get("name", "Unknown"),
                                    currency_id=currency_id,
                                    price_local=price_local,
                                    price_gold=price_gold,
                                    amount=amount,
                                    transaction_type="SELL"
                                )
                                best_offers.append(market_offer)
                                
                        except (ValueError, TypeError):
                            continue
                
                if best_offers:
                    # Sortuj według ceny w GOLD
                    best_offers.sort(key=lambda x: x.price_gold)
                    
                    # Weź 5 najtańszych dla statystyk
                    top_offers = best_offers[:5]
                    prices = [offer.price_gold for offer in top_offers]
                    
                    cheapest_items[item_id] = CheapestItemInfo(
                        item_id=item_id,
                        item_name=item_name,
                        min_price_gold=min(prices),
                        avg_price_gold=sum(prices) / len(prices),
                        best_country=best_offers[0].country_name,
                        best_currency=f"Currency {best_offers[0].currency_id}",
                        amount_available=sum(offer.amount for offer in top_offers),
                        price_history=prices
                    )
                    
            except Exception as e:
                print(f"Error processing item {item_name}: {e}")
                continue
        
        return cheapest_items
    
    def _get_item_offers_in_country(self, item_id: int, country_id: int) -> List[Dict[str, Any]]:
        """Pobiera oferty towaru w konkretnym kraju"""
        try:
            cache_key = f"item_{item_id}_country_{country_id}"
            
            # Sprawdź cache (5 minut)
            if (cache_key in self._market_cache and 
                cache_key in self._cache_timestamp and
                (datetime.now() - self._cache_timestamp[cache_key]).seconds < 300):
                return self._market_cache[cache_key]
            
            # Pobierz z API
            url = f"market/item/get?item_id={item_id}&country_id={country_id}&transaction=SELL"
            response = fetch_data(url, f"item {item_id} offers in country {country_id}")
            
            if response and response.get("code") == 200:
                offers = response.get("data", [])
                
                # Zapisz w cache
                self._market_cache[cache_key] = offers
                self._cache_timestamp[cache_key] = datetime.now()
                
                return offers
            
        except Exception as e:
            print(f"Error fetching offers for item {item_id} in country {country_id}: {e}")
        
        return []
    
    def analyze_item_market(self, item_id: int, item_name: str,
                          countries: Dict[int, Dict[str, Any]],
                          currency_rates: Dict[int, float],
                          gold_id: int) -> Optional[MarketAnalysis]:
        """
        Przeprowadza analizę rynku dla konkretnego towaru.
        
        Args:
            item_id: ID towaru
            item_name: Nazwa towaru
            countries: Słownik krajów
            currency_rates: Kursy walut
            gold_id: ID waluty GOLD
            
        Returns:
            Analiza rynku lub None jeśli brak danych
        """
        try:
            all_offers = []
            
            # Zbierz oferty ze wszystkich krajów
            for country_id, country_info in countries.items():
                offers = self._get_item_offers_in_country(item_id, country_id)
                
                if not offers:
                    continue
                
                # Przelicz na GOLD
                currency_id = country_info.get("currency_id")
                rate = 1.0 if currency_id == gold_id else currency_rates.get(currency_id, 0)
                
                if rate <= 0:
                    continue
                
                for offer in offers:
                    try:
                        price_local = float(offer.get("value", 0))
                        amount = int(offer.get("amount", 0))
                        
                        if price_local > 0 and amount > 0:
                            price_gold = price_local * rate
                            all_offers.append({
                                'price_gold': price_gold,
                                'amount': amount,
                                'country': country_info.get("name", "Unknown")
                            })
                    except (ValueError, TypeError):
                        continue
            
            if not all_offers:
                return None
            
            # Oblicz statystyki
            prices = [offer['price_gold'] for offer in all_offers]
            amounts = [offer['amount'] for offer in all_offers]
            
            # Grupuj według krajów
            country_prices = {}
            for offer in all_offers:
                country = offer['country']
                if country not in country_prices:
                    country_prices[country] = []
                country_prices[country].append(offer['price_gold'])
            
            # Znajdź najlepsze kraje (średnia cena)
            best_countries = []
            for country, country_price_list in country_prices.items():
                avg_price = sum(country_price_list) / len(country_price_list)
                best_countries.append((country, avg_price))
            
            best_countries.sort(key=lambda x: x[1])  # Sortuj według ceny
            
            # Oblicz zmienność cen (odchylenie standardowe)
            avg_price = sum(prices) / len(prices)
            variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
            volatility = variance ** 0.5
            
            # Mediana
            sorted_prices = sorted(prices)
            n = len(sorted_prices)
            median_price = (sorted_prices[n//2] + sorted_prices[(n-1)//2]) / 2
            
            return MarketAnalysis(
                item_name=item_name,
                total_offers=len(all_offers),
                cheapest_price=min(prices),
                most_expensive_price=max(prices),
                average_price=avg_price,
                median_price=median_price,
                best_countries=best_countries[:5],  # Top 5 krajów
                market_depth=sum(amounts),
                price_volatility=volatility
            )
            
        except Exception as e:
            print(f"Error analyzing market for {item_name}: {e}")
            return None
    
    def find_arbitrage_opportunities_items(self, 
                                         countries: Dict[int, Dict[str, Any]],
                                         items: Dict[int, str],
                                         currency_rates: Dict[int, float],
                                         gold_id: int,
                                         min_profit_percent: float = 10.0,
                                         max_opportunities: int = 20) -> List[Dict[str, Any]]:
        """
        Znajduje okazje arbitrażowe dla towarów między krajami.
        
        Args:
            countries: Słownik krajów
            items: Słownik towarów
            currency_rates: Kursy walut
            gold_id: ID waluty GOLD
            min_profit_percent: Minimalny zysk procentowy
            max_opportunities: Maksymalna liczba okazji
            
        Returns:
            Lista okazji arbitrażowych
        """
        opportunities = []
        
        for item_id, item_name in items.items():
            try:
                # Pobierz ceny w różnych krajach
                country_prices = {}
                
                for country_id, country_info in countries.items():
                    offers = self._get_item_offers_in_country(item_id, country_id)
                    
                    if not offers:
                        continue
                    
                    # Przelicz na GOLD
                    currency_id = country_info.get("currency_id")
                    rate = 1.0 if currency_id == gold_id else currency_rates.get(currency_id, 0)
                    
                    if rate <= 0:
                        continue
                    
                    # Znajdź najniższą cenę w tym kraju
                    min_price_local = min(float(offer.get("value", float('inf'))) for offer in offers)
                    if min_price_local < float('inf'):
                        min_price_gold = min_price_local * rate
                        country_prices[country_id] = {
                            'price_gold': min_price_gold,
                            'country_name': country_info.get("name", "Unknown"),
                            'currency_id': currency_id
                        }
                
                if len(country_prices) < 2:
                    continue
                
                # Znajdź możliwości arbitrażu
                countries_list = list(country_prices.items())
                for i in range(len(countries_list)):
                    for j in range(i + 1, len(countries_list)):
                        country1_id, country1_data = countries_list[i]
                        country2_id, country2_data = countries_list[j]
                        
                        price1 = country1_data['price_gold']
                        price2 = country2_data['price_gold']
                        
                        # Oblicz zysk
                        if price1 < price2:
                            profit_percent = ((price2 - price1) / price1) * 100
                            if profit_percent >= min_profit_percent:
                                opportunities.append({
                                    'item_id': item_id,
                                    'item_name': item_name,
                                    'buy_country': country1_data['country_name'],
                                    'sell_country': country2_data['country_name'],
                                    'buy_price_gold': price1,
                                    'sell_price_gold': price2,
                                    'profit_gold': price2 - price1,
                                    'profit_percent': profit_percent
                                })
                        elif price2 < price1:
                            profit_percent = ((price1 - price2) / price2) * 100
                            if profit_percent >= min_profit_percent:
                                opportunities.append({
                                    'item_id': item_id,
                                    'item_name': item_name,
                                    'buy_country': country2_data['country_name'],
                                    'sell_country': country1_data['country_name'],
                                    'buy_price_gold': price2,
                                    'sell_price_gold': price1,
                                    'profit_gold': price1 - price2,
                                    'profit_percent': profit_percent
                                })
                
            except Exception as e:
                print(f"Error processing arbitrage for {item_name}: {e}")
                continue
        
        # Sortuj według zysku procentowego
        opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        return opportunities[:max_opportunities]
    
    def get_market_depth_analysis(self, item_id: int,
                                countries: Dict[int, Dict[str, Any]],
                                currency_rates: Dict[int, float],
                                gold_id: int) -> Dict[str, Any]:
        """
        Analizuje głębokość rynku dla towaru.
        
        Args:
            item_id: ID towaru
            countries: Słownik krajów
            currency_rates: Kursy walut
            gold_id: ID waluty GOLD
            
        Returns:
            Analiza głębokości rynku
        """
        try:
            total_volume = 0
            price_levels = []
            countries_with_offers = 0
            
            for country_id, country_info in countries.items():
                offers = self._get_item_offers_in_country(item_id, country_id)
                
                if not offers:
                    continue
                
                countries_with_offers += 1
                
                # Przelicz na GOLD
                currency_id = country_info.get("currency_id")
                rate = 1.0 if currency_id == gold_id else currency_rates.get(currency_id, 0)
                
                if rate <= 0:
                    continue
                
                for offer in offers:
                    try:
                        price_local = float(offer.get("value", 0))
                        amount = int(offer.get("amount", 0))
                        
                        if price_local > 0 and amount > 0:
                            price_gold = price_local * rate
                            total_volume += amount
                            price_levels.append({
                                'price': price_gold,
                                'amount': amount,
                                'country': country_info.get("name", "Unknown")
                            })
                    except (ValueError, TypeError):
                        continue
            
            if not price_levels:
                return {
                    'total_volume': 0,
                    'countries_with_offers': 0,
                    'price_levels': 0,
                    'liquidity_score': 0
                }
            
            # Sortuj według ceny
            price_levels.sort(key=lambda x: x['price'])
            
            # Oblicz score płynności (im więcej krajów i większy wolumen, tym lepiej)
            liquidity_score = (countries_with_offers * 10) + (total_volume / 1000)
            
            return {
                'total_volume': total_volume,
                'countries_with_offers': countries_with_offers,
                'price_levels': len(price_levels),
                'liquidity_score': liquidity_score,
                'cheapest_price': price_levels[0]['price'] if price_levels else 0,
                'most_expensive_price': price_levels[-1]['price'] if price_levels else 0,
                'price_range': price_levels[-1]['price'] - price_levels[0]['price'] if len(price_levels) > 1 else 0
            }
            
        except Exception as e:
            print(f"Error analyzing market depth: {e}")
            return {
                'total_volume': 0,
                'countries_with_offers': 0,
                'price_levels': 0,
                'liquidity_score': 0
            }
    
    def clear_cache(self):
        """Czyści cache rynkowy"""
        self._market_cache.clear()
        self._cache_timestamp.clear()
    
    def fetch_best_jobs_from_all_countries(self,
                                          countries: Dict[int, Dict[str, Any]], 
                                          currency_rates: Dict[int, float], 
                                          gold_id: int) -> List[JobOffer]:
        """
        Pobiera najlepsze oferty pracy ze wszystkich krajów używając centralnego serwisu.
        Poprawia błąd z job_title = business_id.
        
        Args:
            countries: Słownik krajów
            currency_rates: Kursy walut względem GOLD
            gold_id: ID waluty GOLD
            
        Returns:
            Lista prawidłowo sformatowanych ofert pracy
        """
        all_jobs = []
        
        for country_id, country_info in countries.items():
            try:
                # Pobierz oferty pracy w danym kraju
                url = f"market/jobs/get?country_id={country_id}"
                res = fetch_data(url, f"ofertach pracy w kraju {country_info.get('name', country_id)}")
                
                if res and res.get("code") == 200:
                    offers = res.get("data", [])
                    if offers:
                        # Zbierz oferty z tego kraju
                        country_jobs = []
                        for offer in offers:
                            salary = offer.get("value")  # API uses "value" not "salary"
                            if not salary:
                                continue
                                
                            try:
                                salary_f = float(salary)
                            except (ValueError, TypeError):
                                continue
                            
                            # Przelicz na GOLD
                            currency_id = country_info.get("currency_id")
                            if currency_id == gold_id:
                                salary_gold = salary_f
                            else:
                                rate = currency_rates.get(currency_id)
                                if not rate or rate <= 0:
                                    continue
                                salary_gold = salary_f * rate
                            
                            # ✅ POPRAWKA: Stwórz prawidłowy job_title
                            business_id = offer.get("business_id", "N/A")
                            if business_id != "N/A":
                                job_title = f"Business #{business_id}"
                            else:
                                job_title = "Job Offer"
                            
                            job_offer = JobOffer(
                                country_id=country_id,
                                country_name=country_info.get("name", f"Country {country_id}"),
                                currency_id=currency_id,
                                currency_name=country_info.get("currency_name", f"Currency {currency_id}"),
                                business_id=business_id,
                                salary_local=salary_f,
                                salary_gold=salary_gold,
                                amount=offer.get("amount", 1),
                                economic_skill=offer.get("economic_skill", 0),
                                job_title=job_title
                            )
                            
                            country_jobs.append(job_offer)
                        
                        # Sortuj oferty w tym kraju od najwyższej płacy
                        country_jobs.sort(key=lambda x: x.salary_gold, reverse=True)
                        
                        # Dodaj posortowane oferty z tego kraju do listy głównej
                        all_jobs.extend(country_jobs)
                            
            except Exception as e:
                print(f"Error fetching job offers from country {country_id}: {e}")
                continue
        
        print(f"💼 Znaleziono łącznie {len(all_jobs)} ofert pracy ze wszystkich krajów")
        
        return all_jobs
    
    def convert_job_offers_to_legacy_format(self, job_offers: List[JobOffer]) -> List[Dict[str, Any]]:
        """
        Konwertuje JobOffer dataclass do starszego formatu dict dla kompatybilności wstecznej.
        
        Args:
            job_offers: Lista JobOffer obiektów
            
        Returns:
            Lista słowników w starym formacie
        """
        legacy_jobs = []
        
        for job in job_offers:
            legacy_job = {
                "country_id": job.country_id,
                "country_name": job.country_name,
                "wage_original": job.salary_local,  # Fix: use wage_original not salary_original
                "wage_gold": job.salary_gold,       # Fix: use wage_gold not salary_gold
                "currency_id": job.currency_id,
                "currency_name": job.currency_name,
                "job_title": job.job_title,
                "business_name": job.job_title,     # Use job_title as business_name
                "business_id": job.business_id,
                "company_id": "N/A"  # Nie używane w API
            }
            legacy_jobs.append(legacy_job)
        
        return legacy_jobs

    def get_cache_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki cache"""
        return {
            'cached_requests': len(self._market_cache),
            'oldest_entry': min(self._cache_timestamp.values()) if self._cache_timestamp else None,
            'newest_entry': max(self._cache_timestamp.values()) if self._cache_timestamp else None
        }
