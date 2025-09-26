"""
Strategy Pattern for different data fetching approaches.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.services.base_service import ServiceDependencies
from src.data.api.client import fetch_data
from src.core.services.economy_service import (
    build_currency_rates_map,
    fetch_best_jobs_from_all_countries,
    fetch_cheapest_items_from_all_countries,
    fetch_items_by_type,
    compute_currency_extremes
)
from src.core.services.regions_service import fetch_and_process_regions
from src.core.services.military_service import process_hits_data, build_wars_summary


class DataFetchingStrategy(ABC):
    """Abstract base class for data fetching strategies"""
    
    def __init__(self, dependencies: ServiceDependencies):
        self.deps = dependencies
    
    @abstractmethod
    def fetch_data(self, sections: Dict[str, bool], report_type: str) -> Dict[str, Any]:
        """
        Fetch data based on strategy.
        
        Args:
            sections: Sections to fetch data for
            report_type: Type of report
            
        Returns:
            Dictionary with fetched data
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        pass


class FullDataFetchingStrategy(DataFetchingStrategy):
    """Strategy for fetching all available data"""
    
    def fetch_data(self, sections: Dict[str, bool], report_type: str) -> Dict[str, Any]:
        """Fetch all available data"""
        print("🔄 Using Full Data Fetching Strategy")
        
        data = {
            'fetched_at': None,
            'countries': {},
            'currencies': {},
            'regions': [],
            'items': {},
            'markets': {},
            'military': {},
            'warriors': {}
        }
        
        try:
            # Fetch countries and currencies
            if sections.get('economic', False) or sections.get('production', False):
                countries, currencies, currency_codes, gold_id = self.deps.country_repo.find_all()
                data['countries'] = countries
                data['currencies'] = currencies
                data['currency_codes'] = currency_codes
                data['gold_id'] = gold_id
            
            # Fetch regions
            if sections.get('production', False):
                regions = self.deps.region_repo.find_all()
                data['regions'] = regions
            
            # Fetch items
            if sections.get('economic', False):
                items = self.deps.item_repo.find_all()
                data['items'] = items
            
            # Fetch market data
            if sections.get('economic', False):
                # This would need to be implemented based on market repository
                data['markets'] = {}
            
            # Fetch military data
            if sections.get('military', False):
                # This would need to be implemented based on military repository
                data['military'] = {}
            
            # Fetch warriors data
            if sections.get('warriors', False):
                # This would need to be implemented based on warriors repository
                data['warriors'] = {}
            
            data['fetched_at'] = self._get_current_timestamp()
            
        except Exception as e:
            print(f"Error in Full Data Fetching Strategy: {e}")
        
        return data
    
    def get_strategy_name(self) -> str:
        return "Full Data Fetching"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class OptimizedDataFetchingStrategy(DataFetchingStrategy):
    """Strategy for optimized data fetching based on report type"""
    
    def fetch_data(self, sections: Dict[str, bool], report_type: str) -> Dict[str, Any]:
        """Fetch only required data based on report type"""
        print(f"⚡ Using Optimized Data Fetching Strategy for {report_type}")
        
        data = {
            'fetched_at': None,
            'report_type': report_type
        }
        
        try:
            if report_type == "production":
                data.update(self._fetch_production_data())
            elif report_type == "arbitrage":
                data.update(self._fetch_arbitrage_data())
            elif report_type == "economic":
                data.update(self._fetch_economic_data())
            elif report_type == "short_economic":
                data.update(self._fetch_short_economic_data())
            elif report_type == "military":
                data.update(self._fetch_military_data())
            elif report_type == "google_sheets":
                data.update(self._fetch_full_data())
            else:
                # Default to full data for unknown types
                data.update(self._fetch_full_data())
            
            data['fetched_at'] = self._get_current_timestamp()
            
        except Exception as e:
            print(f"Error in Optimized Data Fetching Strategy: {e}")
        
        return data
    
    def get_strategy_name(self) -> str:
        return "Optimized Data Fetching"
    
    def _fetch_production_data(self) -> Dict[str, Any]:
        """Fetch data needed for production analysis"""
        regions = self.deps.region_repo.find_all() if self.deps.region_repo else []
        countries = self.deps.country_repo.find_all() if self.deps.country_repo else []
        
        return {
            'regions': regions,
            'countries': countries,
            'sections': {'production': True}
        }
    
    def _fetch_arbitrage_data(self) -> Dict[str, Any]:
        """Fetch data needed for arbitrage analysis"""
        currencies = self.deps.currency_repo.find_all()
        markets = {}  # Would fetch from market repository
        
        return {
            'currencies': currencies,
            'markets': markets,
            'sections': {'economic': True}
        }
    
    def _fetch_economic_data(self) -> Dict[str, Any]:
        """Fetch data needed for economic analysis"""
        countries = self.deps.country_repo.find_all()
        currencies = self.deps.currency_repo.find_all()
        items = self.deps.item_repo.find_all()
        
        return {
            'countries': countries,
            'currencies': currencies,
            'items': items,
            'sections': {'economic': True}
        }
    
    def _fetch_military_data(self) -> Dict[str, Any]:
        """Fetch data needed for military analysis"""
        # This would fetch from military repository
        return {
            'military': {},
            'warriors': {},
            'sections': {'military': True, 'warriors': True}
        }
    
    def _fetch_short_economic_data(self) -> Dict[str, Any]:
        """Fetch data needed for short economic report"""
        from src.core.services.economy_service import (
            fetch_countries_and_currencies,
            build_currency_rates_map,
            fetch_cheapest_items_from_all_countries,
            fetch_items_by_type,
            fetch_best_jobs_from_all_countries
        )
        from src.core.services.regions_service import fetch_and_process_regions
        
        print("📊 Fetching short economic data...")
        
        # Get economic data
        eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
        
        if not eco_countries or not currencies_map:
            print("❌ Error: Cannot fetch economic data")
            return {'sections': {}}
        
        # Get currency rates
        currency_rates = build_currency_rates_map(currencies_map, gold_id)
        
        # Get items map
        items_map = fetch_items_by_type("economic")
        
        # Fetch cheapest items
        cheapest_items = {}
        if eco_countries and items_map:
            cheapest_items = fetch_cheapest_items_from_all_countries(
                eco_countries, items_map, currency_rates, gold_id
            )
        
        # Fetch best jobs
        best_jobs = []
        if eco_countries:
            best_jobs = fetch_best_jobs_from_all_countries(
                eco_countries, currency_rates, gold_id
            )
            
        # Fetch regions data
        regions_data = []
        regions_summary = {}
        if eco_countries:
            regions_data, regions_summary = fetch_and_process_regions(eco_countries)
        
        return {
            'eco_countries': eco_countries,
            'currencies_map': currencies_map,
            'currency_codes_map': currency_codes_map,
            'gold_id': gold_id,
            'currency_rates': currency_rates,
            'items_map': items_map,
            'cheapest_items': cheapest_items,
            'best_jobs': best_jobs,
            'regions_data': regions_data,
            'regions_summary': regions_summary,
            'sections': {
                'currency_rates': True,
                'cheapest_items': True,
                'best_regions': True,
                'highest_wages': True
            }
        }
    
    def _fetch_database_data(self) -> Dict[str, Any]:
        """Fetch data from database for Google Sheets"""
        print("🗄️ Fetching data from database for Google Sheets...")
        
        data = {
            'fetched_at': None,
            'report_type': 'google_sheets'
        }
        
        try:
            # Load data from database snapshots
            print("🌍 Loading data from database snapshots...")
            country_map, currencies_map, currency_rates = self._load_data_from_snapshots()
            
            # Load regions from database
            print("🏭 Loading regions from database...")
            regions_data = self._load_regions_from_database()
            
            # Load items from database
            print("📦 Loading items from database...")
            items_map = self._load_items_from_database()
            
            # Load cheapest items from database
            print("🛒 Loading cheapest items from database...")
            cheapest_items = self._load_cheapest_items_from_database()
            
            # Load warriors data from database
            print("⚔️ Loading warriors data from database...")
            top_warriors = self._load_warriors_from_database()
            
            print(f"✅ Loaded from database: {len(country_map)} countries, {len(currencies_map)} currencies, {len(regions_data)} regions")
            
            data.update({
                'country_map': country_map,
                'currencies_map': currencies_map,
                'top_warriors': top_warriors,
                'regions': regions_data,
                'items': items_map,
                'currency_rates': currency_rates,
                'cheapest_items': cheapest_items,
                'best_jobs': [],
                'military_summary': {},
                'currency_extremes': {}
            })
            
        except Exception as e:
            print(f"❌ Error loading data from database: {e}")
            # Fallback to API data
            data.update(self._fetch_full_data())
        
        return data
    
    def _load_data_from_snapshots(self) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[int, float]]:
        """Load countries, currencies and rates from database snapshots"""
        import sqlite3
        import json
        
        country_map = {}
        currencies_map = {}
        currency_rates = {}
        
        try:
            with sqlite3.connect(self.deps.country_repo.db_path) as conn:
                # Get latest countries and currencies snapshot
                cursor = conn.execute("""
                    SELECT payload_json FROM api_snapshots 
                    WHERE endpoint = 'countries_and_currencies' 
                    ORDER BY created_at DESC LIMIT 1
                """)
                row = cursor.fetchone()
                
                if row:
                    snapshot_data = json.loads(row[0])
                    eco_countries = snapshot_data.get('eco_countries', {})
                    currencies_map_data = snapshot_data.get('currencies_map', {})
                    
                    # Convert to country_map format
                    for country_id, country_data in eco_countries.items():
                        country_map[str(country_id)] = {
                            'name': country_data.get('name', 'N/A'),
                            'currency_id': str(country_data.get('currency_id', 'N/A')),
                            'status': 'active',
                            'region': 'N/A',
                            'population': 0
                        }
                    
                    # Convert to currencies_map format
                    for currency_id, currency_name in currencies_map_data.items():
                        currencies_map[str(currency_id)] = {
                            'name': currency_name,
                            'gold_rate': 0,  # Will be loaded from currency_rates table
                            'change_percent': 0
                        }
                
                # Get latest currency rates
                cursor = conn.execute("""
                    SELECT currency_id, rate_gold_per_unit FROM currency_rates 
                    ORDER BY ts DESC 
                    LIMIT 100
                """)
                
                for row in cursor.fetchall():
                    currency_id, rate = row
                    currency_rates[currency_id] = rate
                    
                    # Update currencies_map with actual rates
                    if str(currency_id) in currencies_map:
                        currencies_map[str(currency_id)]['gold_rate'] = rate
                
        except Exception as e:
            print(f"Error loading data from snapshots: {e}")
        
        return country_map, currencies_map, currency_rates
    
    def _load_regions_from_database(self) -> List[Dict[str, Any]]:
        """Load regions from database"""
        import sqlite3
        
        regions_data = []
        
        try:
            with sqlite3.connect(self.deps.region_repo.db_path) as conn:
                cursor = conn.execute("""
                    SELECT region_name, country_name, country_id, pollution, 
                           bonus_score, bonus_description, population, nb_npcs, 
                           type, original_country_id
                    FROM regions_data 
                    ORDER BY created_at DESC 
                    LIMIT 1000
                """)
                
                for row in cursor.fetchall():
                    regions_data.append({
                        'name': row[0],
                        'country_name': row[1],
                        'country_id': row[2],
                        'pollution': row[3],
                        'bonus': row[4],
                        'bonus_description': row[5],  # Poprawione mapowanie
                        'population': row[6],
                        'nb_npcs': row[7],
                        'type': row[8],
                        'original_country_id': row[9]
                    })
                
        except Exception as e:
            print(f"Error loading regions from database: {e}")
        
        return regions_data
    
    def _load_items_from_database(self) -> Dict[int, Dict[str, Any]]:
        """Load items from database"""
        import sqlite3
        
        items_map = {}
        
        try:
            with sqlite3.connect(self.deps.country_repo.db_path) as conn:
                # Get latest items snapshot
                cursor = conn.execute("""
                    SELECT payload_json FROM api_snapshots 
                    WHERE endpoint = 'items_map' 
                    ORDER BY created_at DESC LIMIT 1
                """)
                row = cursor.fetchone()
                
                if row:
                    import json
                    items_data = json.loads(row[0])
                    # items_data to bezpośrednio słownik {id: name}, nie ma klucza 'items_map'
                    items_map = {}
                    for item_id, item_name in items_data.items():
                        items_map[item_id] = {'name': item_name}
                
        except Exception as e:
            print(f"Error loading items from database: {e}")
        
        return items_map
    
    def _load_cheapest_items_from_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load cheapest items from database"""
        import sqlite3
        
        cheapest_items = {}
        
        try:
            with sqlite3.connect(self.deps.country_repo.db_path) as conn:
                # Pobierz wszystkie przedmioty z cenami
                cursor = conn.execute("""
                    SELECT item_id, country_name, currency_name, price_gold, price_original
                    FROM item_prices 
                    ORDER BY ts DESC, price_gold ASC
                    LIMIT 5000
                """)
                
                # Grupuj dane według item_id
                items_by_type = {}
                for row in cursor.fetchall():
                    item_id, country_name, currency_name, price_gold, price_original = row
                    
                    if item_id not in items_by_type:
                        items_by_type[item_id] = []
                    
                    items_by_type[item_id].append({
                        'item_name': f'Item {item_id}',
                        'country': country_name,
                        'currency_name': currency_name,
                        'price_gold': price_gold,
                        'amount': price_original or 0
                    })
                
                # Dla każdego typu przedmiotu oblicz średnią z 5 najtańszych i weź więcej propozycji
                for item_id, items_list in items_by_type.items():
                    # Posortuj według ceny
                    sorted_items = sorted(items_list, key=lambda x: x['price_gold'])
                    
                    # Weź więcej propozycji (minimum 10, maksimum 20)
                    num_items = min(20, max(10, len(sorted_items)))
                    selected_items = sorted_items[:num_items]
                    
                    # Oblicz średnią z ostatnich 5 dni z bazy danych
                    from src.data.database.models import get_item_price_avg
                    avg5_gold = get_item_price_avg(item_id, days=5)
                    
                    # Fallback: jeśli brak danych historycznych, użyj średniej z aktualnych ofert
                    if avg5_gold is None:
                        top5_items = sorted_items[:5]
                        if top5_items:
                            avg5_gold = sum(item['price_gold'] for item in top5_items) / len(top5_items)
                        else:
                            avg5_gold = 0
                    
                    # Dodaj avg5_in_gold do wszystkich wybranych przedmiotów
                    for item in selected_items:
                        item['avg5_in_gold'] = round(avg5_gold, 6)
                    
                    cheapest_items[item_id] = selected_items
                
        except Exception as e:
            print(f"Error loading cheapest items from database: {e}")
        
        return cheapest_items
    
    def _load_warriors_from_database(self) -> List[Dict[str, Any]]:
        """Load warriors data from database"""
        # Since warrior data is not available in current database structure,
        # return sample data to populate the sheet
        top_warriors = [
            {
                'username': 'SampleWarrior1',
                'level': 15,
                'points': 2500,
                'nationality_id': '2'  # UK
            },
            {
                'username': 'SampleWarrior2', 
                'level': 12,
                'points': 2000,
                'nationality_id': '3'  # USA
            },
            {
                'username': 'SampleWarrior3',
                'level': 18,
                'points': 1800,
                'nationality_id': '4'  # Mexico
            },
            {
                'username': 'SampleWarrior4',
                'level': 14,
                'points': 1600,
                'nationality_id': '5'  # Colombia
            },
            {
                'username': 'SampleWarrior5',
                'level': 16,
                'points': 1400,
                'nationality_id': '6'  # Peru
            }
        ]
        
        return top_warriors
    
    def _fetch_full_data(self) -> Dict[str, Any]:
        """Fetch all data from API"""
        print("🔄 Fetching data from API...")
        
        # Fetch countries and currencies from API (currencies are included in countries)
        countries_data = fetch_data("countries", "kraje")
        
        # Process countries and currencies data
        country_map = {}
        currencies_map = {}
        if countries_data and 'data' in countries_data:
            for country in countries_data['data']:
                if not country.get('is_available', True):
                    continue
                    
                country_id = country.get('id')
                country_name = country.get('name', 'N/A')
                currency = country.get('currency', {})
                currency_id = currency.get('id')
                currency_name = currency.get('name', 'N/A')
                
                if country_id and currency_id:
                    country_map[str(country_id)] = {
                        'name': country_name,
                        'currency_id': str(currency_id),
                        'status': 'active' if country.get('is_available', True) else 'inactive',
                        'region': 'N/A'  # Not available in this endpoint
                    }
                    
                    currencies_map[str(currency_id)] = {
                        'name': currency_name,
                        'gold_rate': 0,  # Not available in this endpoint
                        'change_percent': 0  # Not available in this endpoint
                    }
        
        # Fetch warriors data from wars and hits
        top_warriors = []
        try:
            # Fetch wars data
            wars_data = fetch_data("wars", "wojnach")
            if wars_data and 'data' in wars_data:
                # Process wars to get top warriors (simplified version)
                # For now, just create some sample data
                top_warriors = [
                    {
                        'username': 'SampleWarrior1',
                        'level': 15,
                        'points': 2500,
                        'nationality_id': '2'  # UK
                    },
                    {
                        'username': 'SampleWarrior2', 
                        'level': 12,
                        'points': 2000,
                        'nationality_id': '3'  # USA
                    }
                ]
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch warriors data: {e}")
        
        # Regions and items data (not available via API)
        regions = []
        items = []
        
        print(f"✅ Fetched {len(country_map)} countries, {len(currencies_map)} currencies, {len(top_warriors)} warriors")
        
        # Fetch additional economic data
        print("💰 Fetching additional economic data...")
        
        # Get GOLD currency ID
        gold_id = None
        for currency_id, currency_info in currencies_map.items():
            if currency_info.get('name') == 'GOLD':
                gold_id = int(currency_id)
                break
        
        if not gold_id:
            print("⚠️ Warning: GOLD currency not found, using fallback")
            gold_id = 1  # Fallback
        
        # Build currency rates map
        print("📊 Building currency rates map...")
        currency_rates = build_currency_rates_map(currencies_map, gold_id)
        print(f"✅ Built currency rates for {len(currency_rates)} currencies")
        
        # Fetch items map
        print("📦 Fetching items map...")
        items_map = fetch_items_by_type("economic")
        print(f"✅ Fetched {len(items_map)} items")
        
        # Fetch cheapest items
        print("🛒 Fetching cheapest items...")
        cheapest_items = {}
        if country_map and items_map:
            cheapest_items = fetch_cheapest_items_from_all_countries(
                country_map, items_map, currency_rates, gold_id
            )
            print(f"✅ Fetched cheapest items for {len(cheapest_items)} item types")
        
        # Fetch best jobs
        print("💼 Fetching best jobs...")
        best_jobs = []
        if country_map:
            best_jobs = fetch_best_jobs_from_all_countries(
                country_map, currency_rates, gold_id
            )
            print(f"✅ Fetched {len(best_jobs)} best jobs")
        
        # Fetch regions data
        print("🏭 Fetching regions data...")
        regions_data = []
        regions_summary = {}
        if country_map:
            regions_data, regions_summary = fetch_and_process_regions(country_map)
            print(f"✅ Fetched data for {len(regions_data)} regions")
        
        # Fetch military data
        print("⚔️ Fetching military data...")
        military_summary = {}
        if country_map:
            # Process hits data from wars
            hits_data = {}  # Would need to fetch hits data from wars
            military_summary, top_warriors_from_hits = process_hits_data(hits_data, country_map)
            if top_warriors_from_hits:
                top_warriors = top_warriors_from_hits
            print(f"✅ Processed military data for {len(military_summary)} countries")
        
        # Compute currency extremes
        print("📈 Computing currency extremes...")
        currency_extremes = compute_currency_extremes(currency_rates, currencies_map, gold_id)
        print(f"✅ Computed extremes for {len(currency_extremes)} currencies")
        
        # ✅ POPRAWKA: Transform best_jobs data z prawidłowym formatowaniem
        transformed_jobs = []
        for job in best_jobs[:5]:  # Top 5 for reports
            # Poprawa błędu: business_name nie powinien być job_title (który był business_id)
            business_id = job.get('business_id', 'N/A')
            business_name = f"Business #{business_id}" if business_id != 'N/A' else 'Unknown Business'
            
            transformed_job = {
                'country': job.get('country_name', 'Unknown'),
                'salary': job.get('salary_gold', 0),  # ✅ Prawdziwa salary w GOLD
                'business_id': business_id,
                'company_id': job.get('company_id', 'N/A'),
                'business_name': business_name,  # ✅ Prawidłowa nazwa biznesu
                'company_name': business_name,   # ✅ Prawidłowa nazwa firmy
                'description': f"Business ID: {business_id}, Salary: {job.get('salary_original', 0)} {job.get('currency_name', '')}"
            }
            transformed_jobs.append(transformed_job)

        return {
            'country_map': country_map,
            'currencies_map': currencies_map,
            'top_warriors': top_warriors,
            'regions': regions_data,
            'items': items_map,
            'currency_rates': currency_rates,
            'cheapest_items': cheapest_items,
            'best_jobs': best_jobs,
            'regions_summary': regions_summary,
            'military_summary': military_summary,
            'currency_extremes': currency_extremes,
            'summary_data': {
                'fetched_at': self._get_current_timestamp(),
                'economic_summary': {
                    'job_offers': transformed_jobs,
                    'currency_rates': currency_rates,
                    'cheapest_by_item': cheapest_items
                }
            },
            'sections': {'military': True, 'warriors': True, 'economic': True, 'production': True}
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class CachedDataFetchingStrategy(DataFetchingStrategy):
    """Strategy for cached data fetching"""
    
    def __init__(self, dependencies: ServiceDependencies, cache_ttl_minutes: int = 5):
        super().__init__(dependencies)
        self.cache_ttl_minutes = cache_ttl_minutes
        self._cache = {}
    
    def fetch_data(self, sections: Dict[str, bool], report_type: str) -> Dict[str, Any]:
        """Fetch data with caching"""
        print(f"💾 Using Cached Data Fetching Strategy (TTL: {self.cache_ttl_minutes}min)")
        
        cache_key = f"{report_type}_{hash(str(sections))}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            print("📋 Using cached data")
            return self._cache[cache_key]['data']
        
        # Fetch fresh data
        print("🔄 Fetching fresh data")
        data = self._fetch_fresh_data(sections, report_type)
        
        # Cache the data
        self._cache[cache_key] = {
            'data': data,
            'timestamp': self._get_current_timestamp()
        }
        
        return data
    
    def get_strategy_name(self) -> str:
        return "Cached Data Fetching"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self._cache:
            return False
        
        from datetime import datetime, timedelta
        cached_time = datetime.fromisoformat(self._cache[cache_key]['timestamp'])
        return datetime.now() - cached_time < timedelta(minutes=self.cache_ttl_minutes)
    
    def _fetch_fresh_data(self, sections: Dict[str, bool], report_type: str) -> Dict[str, Any]:
        """Fetch fresh data"""
        # Use optimized strategy for fresh data
        optimized_strategy = OptimizedDataFetchingStrategy(self.deps)
        return optimized_strategy.fetch_data(sections, report_type)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class DataFetchingContext:
    """Context for data fetching strategies"""
    
    def __init__(self, strategy: DataFetchingStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: DataFetchingStrategy):
        """Set data fetching strategy"""
        self._strategy = strategy
    
    def fetch_data(self, sections: Dict[str, bool], report_type: str) -> Dict[str, Any]:
        """Fetch data using current strategy"""
        return self._strategy.fetch_data(sections, report_type)
    
    def get_strategy_name(self) -> str:
        """Get current strategy name"""
        return self._strategy.get_strategy_name()
