"""
Strategy Pattern for different data fetching approaches.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.services.base_service import ServiceDependencies


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
            elif report_type == "military":
                data.update(self._fetch_military_data())
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
        regions = self.deps.region_repo.find_all()
        countries = self.deps.country_repo.find_all()
        
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
    
    def _fetch_full_data(self) -> Dict[str, Any]:
        """Fetch all data"""
        countries = self.deps.country_repo.find_all()
        currencies = self.deps.currency_repo.find_all()
        regions = self.deps.region_repo.find_all()
        items = self.deps.item_repo.find_all()
        
        return {
            'countries': countries,
            'currencies': currencies,
            'regions': regions,
            'items': items,
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
