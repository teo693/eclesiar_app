"""
Refactored Economy Service using Repository Pattern and Service Layer.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .base_service import BaseService
from ..models.entities import Country, Currency, Item
from ..models.repositories import CountryRepository, CurrencyRepository, ItemRepository


class EconomyService(BaseService):
    """Refactored economy service with clean architecture"""
    
    def get_countries_and_currencies(self) -> Tuple[Dict[int, Dict[str, Any]], Dict[int, str], Dict[int, str], Optional[int]]:
        """
        Get countries and currencies data.
        
        Returns:
            Tuple of (countries_dict, currencies_map, currency_codes_map, gold_id)
        """
        try:
            # Get all countries from repository
            countries = self.country_repo.find_all()
            currencies = self.currency_repo.find_all()
            
            # Convert to dictionaries for backward compatibility
            countries_dict = {}
            currencies_map = {}
            currency_codes_map = {}
            gold_id = None
            
            for country in countries:
                countries_dict[country.id] = {
                    'name': country.name,
                    'currency_id': country.currency_id,
                    'currency_name': country.currency_name,
                    'is_available': country.is_available
                }
            
            for currency in currencies:
                currencies_map[currency.id] = currency.name
                currency_codes_map[currency.id] = currency.code
                
                # Find GOLD currency
                if currency.code == 'GOLD' or 'GOLD' in currency.name.upper():
                    gold_id = currency.id
            
            return countries_dict, currencies_map, currency_codes_map, gold_id
            
        except Exception as e:
            print(f"Error getting countries and currencies: {e}")
            return {}, {}, {}, None
    
    def build_currency_rates_map(self, currencies_map: Dict[int, str], gold_id: Optional[int]) -> Dict[int, float]:
        """
        Build currency rates map.
        
        Args:
            currencies_map: Dictionary mapping currency IDs to names
            gold_id: GOLD currency ID
            
        Returns:
            Dictionary mapping currency IDs to rates
        """
        if not gold_id:
            return {}
        
        rates_map = {}
        for currency_id in currencies_map.keys():
            if currency_id == gold_id:
                rates_map[currency_id] = 1.0  # GOLD to GOLD rate
            else:
                # Get latest rate from repository
                rate_history = self.currency_repo.get_currency_rates(currency_id)
                if rate_history:
                    rates_map[currency_id] = rate_history[0][1]  # Latest rate
                else:
                    rates_map[currency_id] = 0.0
        
        return rates_map
    
    def get_cheapest_items_by_type(self, item_type: str) -> List[Item]:
        """
        Get cheapest items by type.
        
        Args:
            item_type: Type of items to find
            
        Returns:
            List of cheapest items
        """
        try:
            items = self.item_repo.find_by_type(item_type)
            # Sort by price and return cheapest
            return sorted(items, key=lambda x: x.price_gold or float('inf'))[:5]
        except Exception as e:
            print(f"Error getting cheapest items: {e}")
            return []
    
    def get_currency_offers(self, currency_id: int) -> Dict[str, Any]:
        """
        Get currency market offers.
        
        Args:
            currency_id: Currency ID
            
        Returns:
            Dictionary with market offers
        """
        try:
            market = self.market_repo.get_currency_market(currency_id)
            if not market:
                return {}
            
            return {
                'currency_id': market.currency_id,
                'currency_name': market.currency_name,
                'buy_offers': [
                    {
                        'rate': offer.rate,
                        'amount': offer.amount,
                        'owner_id': offer.owner_id,
                        'transaction_type': offer.transaction_type.value,
                        'timestamp': offer.timestamp.isoformat()
                    }
                    for offer in market.buy_offers
                ],
                'sell_offers': [
                    {
                        'rate': offer.rate,
                        'amount': offer.amount,
                        'owner_id': offer.owner_id,
                        'transaction_type': offer.transaction_type.value,
                        'timestamp': offer.timestamp.isoformat()
                    }
                    for offer in market.sell_offers
                ],
                'best_buy_rate': market.best_buy_rate,
                'best_sell_rate': market.best_sell_rate
            }
        except Exception as e:
            print(f"Error getting currency offers: {e}")
            return {}
    
    def compute_currency_extremes(self, currency_rates: Dict[int, float]) -> Dict[str, Any]:
        """
        Compute currency rate extremes.
        
        Args:
            currency_rates: Dictionary of currency rates
            
        Returns:
            Dictionary with extremes data
        """
        if not currency_rates:
            return {}
        
        # Find highest and lowest rates
        sorted_rates = sorted(currency_rates.items(), key=lambda x: x[1])
        
        return {
            'highest_rate': {
                'currency_id': sorted_rates[-1][0],
                'rate': sorted_rates[-1][1]
            },
            'lowest_rate': {
                'currency_id': sorted_rates[0][0],
                'rate': sorted_rates[0][1]
            },
            'total_currencies': len(currency_rates),
            'average_rate': sum(currency_rates.values()) / len(currency_rates)
        }
