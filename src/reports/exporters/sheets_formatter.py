"""
Google Sheets Data Formatter

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
from .enhanced_sheets_formatter import EnhancedSheetsFormatter
from src.core.services.calculations import (
    RegionCalculationService,
    CurrencyCalculationService,
    ProductionCalculationService
)

class SheetsFormatter:
    """REFACTORED Formats data for Google Sheets export using centralized services"""
    
    def __init__(self):
        self.date_format = "%Y-%m-%d %H:%M:%S"
        
        # Initialize centralized calculation services
        self.region_calc = RegionCalculationService()
        self.currency_calc = CurrencyCalculationService()
        self.production_calc = ProductionCalculationService()
        
        # Legacy compatibility - keep reference to bonus mapping
        self.bonus_type_mapping = self.region_calc.bonus_type_mapping
    
    def calculate_country_bonus(self, country_name: str, regions_data: List[Dict[str, Any]], item_name: str = "grain") -> float:
        """REFACTORED - Deleguje do centralnego serwisu regionów"""
        return self.region_calc.calculate_country_bonus(country_name, item_name, regions_data)
    
    def _parse_bonus_description(self, bonus_description: str) -> Dict[str, float]:
        """
        Parsuje opis bonusu w formacie "TICKETS:15" lub "WEAPONS:20 TICKETS:15"
        
        Args:
            bonus_description: Opis bonusu z API
            
        Returns:
            Słownik {typ_bonusu: wartość}
        """
        bonus_by_type = {}
        
        if not bonus_description:
            return bonus_by_type
        
        # Podziel na części (np. "WEAPONS:20 TICKETS:15")
        parts = bonus_description.split()
        
        for part in parts:
            if ':' in part:
                try:
                    bonus_type, bonus_value = part.split(':')
                    bonus_by_type[bonus_type] = float(bonus_value)
                except ValueError:
                    continue
        
        return bonus_by_type
    
    def _get_regional_bonus_for_type(self, region: Dict[str, Any], item_name: str) -> float:
        """REFACTORED - Deleguje do centralnego serwisu regionów"""
        try:
            bonus_value, _ = self.region_calc.get_regional_bonus_for_item(region, item_name)
            return bonus_value * 100.0  # Konwersja z ułamka na procenty dla kompatybilności
        except Exception as e:
            print(f"Error getting regional bonus for {item_name}: {e}")
            return 0.0
    
    def format_daily_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """Format daily report data for Google Sheets"""
        sheets_data = {}
        
        # Sheet 1: Podsumowanie
        country_map = data.get('country_map', {})
        currencies_map = data.get('currencies_map', {})
        regions = data.get('regions', [])
        items = data.get('items', {})
        top_warriors = data.get('top_warriors', [])
        currency_rates = data.get('currency_rates', {})
        cheapest_items = data.get('cheapest_items', {})
        
        # Oblicz statystyki
        total_countries = len(country_map)
        total_currencies = len(currencies_map)
        total_regions = len(regions)
        total_items = len(items)
        total_warriors = len(top_warriors)
        total_item_prices = sum(len(items_list) for items_list in cheapest_items.values())
        
        # Znajdź najaktywniejsze kraje (z największą liczbą regionów)
        # Użyj regions_data jeśli dostępne (ma przetworzone nazwy krajów), w przeciwnym razie regions
        regions_for_counting = data.get('regions_data', regions)
        country_region_count = {}
        for region in regions_for_counting:
            country_name = region.get('country_name', 'N/A')
            country_region_count[country_name] = country_region_count.get(country_name, 0) + 1
        
        top_countries = sorted(country_region_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Znajdź najdroższe i najtańsze waluty
        if currency_rates:
            sorted_rates = sorted(currency_rates.items(), key=lambda x: x[1], reverse=True)
            most_expensive = sorted_rates[0] if sorted_rates else (0, 0)
            cheapest = sorted_rates[-1] if sorted_rates else (0, 0)
        else:
            most_expensive = (0, 0)
            cheapest = (0, 0)
        
        sheets_data["Summary"] = [
            ["📊 ECLESIAR REPORT - SUMMARY", ""],
            ["", ""],
            ["📅 Report Information", ""],
            ["Generated at", datetime.now().strftime(self.date_format)],
            ["Report type", data.get('report_type', 'N/A')],
            ["", ""],
            ["📈 General Statistics", ""],
            ["Number of countries", total_countries],
            ["Number of currencies", total_currencies],
            ["Number of production regions", total_regions],
            ["Number of items", total_items],
            ["Number of warriors", total_warriors],
            ["Number of item prices", total_item_prices],
            ["", ""],
            ["🏆 Most active countries (regions)", ""],
        ]
        
        for i, (country, count) in enumerate(top_countries, 1):
            sheets_data["Summary"].append([f"{i}. {country}", f"{count} regions"])
        
        sheets_data["Summary"].extend([
            ["", ""],
            ["💰 Currency rates", ""],
            ["Most expensive currency", f"ID {most_expensive[0]}: {most_expensive[1]:.6f}"],
            ["Currency name", currencies_map.get(str(most_expensive[0]), f'Currency {most_expensive[0]}')],
            ["Cheapest currency", f"ID {cheapest[0]}: {cheapest[1]:.6f}"],
            ["Currency name", currencies_map.get(str(cheapest[0]), f'Currency {cheapest[0]}')],
            ["", ""],
            ["📊 Best production regions", ""],
        ])
        
        # Top 5 regions by bonus
        if regions:
            def get_bonus_score(x):
                score = x.get('bonus_score', 0)
                try:
                    return float(score) if score is not None else 0
                except (ValueError, TypeError):
                    return 0
            
            top_regions = sorted(regions, key=get_bonus_score, reverse=True)[:5]
            for i, region in enumerate(top_regions, 1):
                sheets_data["Summary"].append([
                    f"{i}. {region.get('region_name', region.get('name', 'N/A'))}",
                    f"Bonus: {region.get('bonus_score', 0):.2f} ({region.get('bonus_description', 'N/A')})"
                ])
        
        # Add lowest prices for each item
        if cheapest_items:
            sheets_data["Summary"].extend([
                ["", ""],
                ["🛒 Lowest item prices", ""],
            ])
            
            # Item ID to name mapping
            item_names = {
                1: "Grain",
                2: "Food Q1", 3: "Food Q2", 4: "Food Q3", 5: "Food Q4", 6: "Food Q5",
                7: "Iron",
                8: "Weapon Q1", 9: "Weapon Q2", 10: "Weapon Q3", 11: "Weapon Q4", 12: "Weapon Q5",
                13: "Fuel",
                14: "Tickets Q1", 15: "Tickets Q2", 16: "Tickets Q3", 17: "Tickets Q4", 18: "Tickets Q5",
                19: "Titanium",
                20: "Aircraft Q1", 21: "Aircraft Q2", 22: "Aircraft Q3", 23: "Aircraft Q4", 24: "Aircraft Q5"
            }
            
            for item_id, items_list in cheapest_items.items():
                if items_list:
                    # Find cheapest item of this type
                    cheapest_item = min(items_list, key=lambda x: x.get('price_gold', float('inf')))
                    item_name = item_names.get(item_id, f"Item {item_id}")
                    country = cheapest_item.get('country', 'N/A')
                    price = cheapest_item.get('price_gold', 0)
                    
                    # Poprawne mapowanie nazwy waluty
                    currency_id = cheapest_item.get('currency_id')
                    if currency_id and currencies_map:
                        # Sprawdź różne formaty mapowania walut
                        currency_data = currencies_map.get(str(currency_id)) or currencies_map.get(currency_id)
                        if isinstance(currency_data, dict):
                            currency = currency_data.get('name', cheapest_item.get('currency_name', 'N/A'))
                        elif isinstance(currency_data, str):
                            currency = currency_data
                        else:
                            currency = cheapest_item.get('currency_name', 'N/A')
                    else:
                        currency = cheapest_item.get('currency_name', 'N/A')
                    
                    amount = cheapest_item.get('amount', 0)
                    avg5 = cheapest_item.get('avg5_in_gold', 0)
                    
                    sheets_data["Summary"].append([
                        f"{item_name}",
                        f"{price:.6f}"
                    ])
                    sheets_data["Summary"].append([
                        "Currency",
                        f"{currency}"
                    ])
                    sheets_data["Summary"].append([
                        "Country",
                        f"{country}"
                    ])
                    sheets_data["Summary"].append([
                        "Amount",
                        f"{amount}"
                    ])
                    sheets_data["Summary"].append([
                        "5-day average",
                        f"{avg5:.6f}"
                    ])
        
        # Sheet 2: Currency Rates (with growth indicators)
        currency_rates = data.get('currency_rates', {})
        currencies_map = data.get('currencies_map', {})
        historical_data = data.get('historical_data', {})
        
        if currency_rates:
            rates_data = [["Currency", "Rate vs GOLD", "Previous Rate", "Change %"]]
            
            # Pobierz wczorajsze kursy z danych historycznych
            from datetime import timedelta
            yesterday_key = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterday_rates = {}
            
            try:
                if yesterday_key in historical_data:
                    yesterday_rates = (historical_data[yesterday_key].get('economic_summary') or {}).get('currency_rates') or {}
                
                # Jeśli nie ma wczorajszych danych, szukaj najbliższego poprzedniego dnia
                if not yesterday_rates and historical_data:
                    available_dates = sorted([d for d in historical_data.keys() if d < yesterday_key], reverse=True)
                    for date in available_dates:
                        rates = (historical_data[date].get('economic_summary') or {}).get('currency_rates') or {}
                        if rates:
                            yesterday_rates = rates
                            break
            except Exception as e:
                print(f"DEBUG: Error getting yesterday rates: {e}")
                yesterday_rates = {}
            
            # Sortuj waluty alfabetycznie według nazwy
            def get_currency_name(x):
                currency_id = str(x[0])
                currency_data = currencies_map.get(currency_id, {})
                if isinstance(currency_data, dict):
                    return currency_data.get('name', f'Currency {currency_id}')
                else:
                    return str(currency_data)
            
            sorted_rates = sorted(currency_rates.items(), key=get_currency_name)
            
            for currency_id, rate in sorted_rates:
                currency_data = currencies_map.get(str(currency_id), {})
                if isinstance(currency_data, dict):
                    currency_name = currency_data.get('name', f'Currency {currency_id}')
                else:
                    currency_name = str(currency_data)
                
                # Oblicz wskaźnik wzrostu na podstawie wczorajszych kursów
                growth_text = "—"
                prev_rate_text = "—"
                
                if yesterday_rates:
                    prev_rate = yesterday_rates.get(str(currency_id))
                    if prev_rate is not None and isinstance(rate, (int, float)) and isinstance(prev_rate, (int, float)) and prev_rate > 0:
                        growth_rate = ((rate - prev_rate) / prev_rate) * 100.0
                        arrow = "▲" if growth_rate > 0 else ("▼" if growth_rate < 0 else "→")
                        growth_text = f"{arrow} {growth_rate:+.2f}%"
                        prev_rate_text = f"{prev_rate:.6f}"
                
                rates_data.append([
                    currency_name,
                    f"{rate:.6f}",
                    prev_rate_text,
                    growth_text
                ])
            
            sheets_data["Currency Rates"] = rates_data
        
        # Usunięto duplikację - kursy walut już są wcześniej
        
        
        # Sheet 6: Best Job Offers
        best_jobs = data.get('best_jobs', [])
        if best_jobs:
            jobs_data = [["Country", "Position", "Salary (GOLD)", "Currency", "Region"]]
            for job in best_jobs[:20]:  # Top 20
                jobs_data.append([
                    job.get('country', 'N/A'),
                    job.get('position', 'N/A'),
                    f"{job.get('salary_gold', 0):.6f}",
                    job.get('currency', 'N/A'),
                    job.get('region', 'N/A')
                ])
            sheets_data["Best Jobs"] = jobs_data
        
        # Sheet 4: Production Regions - GRAIN (sorted by productivity)
        regions_data = data.get('regions', [])
        country_map = data.get('country_map', {})
        
        if regions_data:
            # Filtruj regiony które mogą produkować GRAIN (fabryki > 0 lub bonus GRAIN) i deduplikuj
            grain_regions = []
            unique_grain_regions = {}
            for region in regions_data:
                if isinstance(region, dict):
                    # Sprawdź czy region ma fabryki GRAIN lub bonus GRAIN
                    factories = region.get('factories', {})
                    has_grain_factories = factories and factories.get('grain', 0) > 0
                    bonus_description = region.get('bonus_description', '')
                    has_grain_bonus = bonus_description and 'GRAIN:' in bonus_description
                    
                    if has_grain_factories or has_grain_bonus:
                        region_key = region.get('region_name', region.get('name', '')).lower()
                        if region_key and region_key not in unique_grain_regions:
                            unique_grain_regions[region_key] = region
            
            grain_regions = list(unique_grain_regions.values())
            
            if grain_regions:
                regions_sheet = [["Region", "Country", "Regional Bonus", "Pollution", "Bonus Type", "Country Bonus", "Productivity", "Q1", "Q2", "Q3", "Q4", "Q5"]]
                
                # Oblicz produktywność dla każdego regionu GRAIN
                regions_with_productivity = []
                for region in grain_regions:
                    country_name = region.get('country_name', 'N/A')
                    
                    # Oblicz prawdziwy bonus krajowy dla GRAIN
                    country_bonus = self.calculate_country_bonus(country_name, regions_data, "grain")
                    
                    # Pobierz bonus regionalny dla GRAIN
                    regional_bonus = self._get_regional_bonus_for_type(region, "grain")
                    
                    # Upewnij się, że country_bonus i regional_bonus są liczbami
                    if country_bonus is None:
                        country_bonus = 0.0
                    if regional_bonus is None:
                        regional_bonus = 0.0
                    
                    # Oblicz produktywność (bonus regionalny + bonus krajowy)
                    total_productivity = regional_bonus + (country_bonus / 100.0) * 100  # Konwersja na procenty
                    
                    # Upewnij się, że total_productivity jest liczbą
                    if total_productivity is None:
                        total_productivity = 0.0
                    
                    # Debug: sprawdź czy total_productivity jest liczbą
                    if not isinstance(total_productivity, (int, float)):
                        print(f"Warning: total_productivity is not a number: {total_productivity} (type: {type(total_productivity)}) for region {region.get('region_name', 'N/A')}")
                        total_productivity = 0.0
                    
                    # Oblicz produkcję Q1-Q5 na podstawie produktywności
                    base_production = total_productivity
                    q1 = base_production * 0.8
                    q2 = base_production * 0.9
                    q3 = base_production * 1.0
                    q4 = base_production * 1.1
                    q5 = base_production * 1.2
                    
                    regions_with_productivity.append({
                        'region': region,
                        'country_bonus': country_bonus,
                        'regional_bonus': regional_bonus,
                        'total_productivity': float(total_productivity),  # Upewnij się, że to float
                        'q1': q1,
                        'q2': q2,
                        'q3': q3,
                        'q4': q4,
                        'q5': q5
                    })
                
                # Posortuj regiony według produktywności dla GRAIN
                def get_productivity_key(x):
                    if not isinstance(x, dict):
                        return 0
                    productivity = x.get('total_productivity', 0)
                    try:
                        return float(productivity) if productivity is not None else 0
                    except (ValueError, TypeError):
                        return 0
                
                sorted_regions = sorted(regions_with_productivity, key=get_productivity_key, reverse=True)
                
                for region_data in sorted_regions[:max(10, len(sorted_regions))]:  # Minimum 10, maksimum wszystkie dostępne
                    if not isinstance(region_data, dict):
                        continue
                    region = region_data.get('region', {})
                    country_bonus = region_data.get('country_bonus', 0)
                    regional_bonus = region_data.get('regional_bonus', 0)
                    total_productivity = region_data.get('total_productivity', 0)
                    q1 = region_data.get('q1', 0)
                    q2 = region_data.get('q2', 0)
                    q3 = region_data.get('q3', 0)
                    q4 = region_data.get('q4', 0)
                    q5 = region_data.get('q5', 0)
                    
                    regions_sheet.append([
                        region.get('region_name', region.get('name', 'N/A')),
                        region.get('country_name', 'N/A'),
                        f"{regional_bonus:.2f}",
                        f"{region.get('pollution', 0):.2f}",
                        "GRAIN",
                        f"{country_bonus:.2f}%",
                        f"{total_productivity:.2f}%",
                        f"{q1:.1f}",
                        f"{q2:.1f}",
                        f"{q3:.1f}",
                        f"{q4:.1f}",
                        f"{q5:.1f}"
                    ])
                
                sheets_data["Production Regions - GRAIN"] = regions_sheet
        
        # Dodaj arkusze dla innych typów towarów
        item_types = [
            ("WEAPONS", "weapon"),
            ("IRON", "iron"), 
            ("FOOD", "food"),
            ("AIRCRAFT", "aircraft"),
            ("TITANIUM", "titanium"),
            ("FUEL", "fuel"),
            ("TICKETS", "airplane ticket")
        ]
        
        for bonus_type, item_name in item_types:
            # Filtruj regiony które mają bonus dla danego typu i deduplikuj
            type_regions = []
            unique_type_regions = {}
            for region in regions_data:
                if isinstance(region, dict):
                    bonus_description = region.get('bonus_description', '')
                    if bonus_description and f'{bonus_type}:' in bonus_description:
                        region_key = region.get('region_name', region.get('name', '')).lower()
                        if region_key not in unique_type_regions:
                            unique_type_regions[region_key] = region
            
            type_regions = list(unique_type_regions.values())
            
            if type_regions:
                regions_sheet = [["Region", "Country", "Regional Bonus", "Pollution", "Bonus Type", "Country Bonus", "Productivity", "Q1", "Q2", "Q3", "Q4", "Q5"]]
                
                # Oblicz produktywność dla każdego regionu
                regions_with_productivity = []
                for region in type_regions:
                    country_name = region.get('country_name', 'N/A')
                    
                    # Oblicz prawdziwy bonus krajowy dla danego typu
                    country_bonus = self.calculate_country_bonus(country_name, regions_data, item_name)
                    
                    # Pobierz bonus regionalny dla danego typu
                    regional_bonus = self._get_regional_bonus_for_type(region, item_name)
                    
                    # Upewnij się, że country_bonus i regional_bonus są liczbami
                    if country_bonus is None:
                        country_bonus = 0.0
                    if regional_bonus is None:
                        regional_bonus = 0.0
                    
                    # Oblicz produktywność (bonus regionalny + bonus krajowy)
                    total_productivity = regional_bonus + (country_bonus / 100.0) * 100  # Konwersja na procenty
                    
                    # Upewnij się, że total_productivity jest liczbą
                    if total_productivity is None:
                        total_productivity = 0.0
                    
                    # Debug: sprawdź czy total_productivity jest liczbą
                    if not isinstance(total_productivity, (int, float)):
                        print(f"Warning: total_productivity is not a number: {total_productivity} (type: {type(total_productivity)}) for region {region.get('region_name', 'N/A')}")
                        total_productivity = 0.0
                    
                    # Oblicz produkcję Q1-Q5 na podstawie produktywności
                    base_production = total_productivity
                    q1 = base_production * 0.8
                    q2 = base_production * 0.9
                    q3 = base_production * 1.0
                    q4 = base_production * 1.1
                    q5 = base_production * 1.2
                    
                    regions_with_productivity.append({
                        'region': region,
                        'country_bonus': country_bonus,
                        'regional_bonus': regional_bonus,
                        'total_productivity': float(total_productivity),  # Upewnij się, że to float
                        'q1': q1,
                        'q2': q2,
                        'q3': q3,
                        'q4': q4,
                        'q5': q5
                    })
                
                # Posortuj regiony według produktywności dla danego typu
                def get_productivity_key(x):
                    if not isinstance(x, dict):
                        return 0
                    productivity = x.get('total_productivity', 0)
                    try:
                        return float(productivity) if productivity is not None else 0
                    except (ValueError, TypeError):
                        return 0
                sorted_regions = sorted(regions_with_productivity, key=get_productivity_key, reverse=True)
                
                for region_data in sorted_regions[:max(10, len(sorted_regions))]:  # Minimum 10, maksimum wszystkie dostępne
                    if not isinstance(region_data, dict):
                        continue
                    region = region_data.get('region', {})
                    country_bonus = region_data.get('country_bonus', 0)
                    regional_bonus = region_data.get('regional_bonus', 0)
                    total_productivity = region_data.get('total_productivity', 0)
                    q1 = region_data.get('q1', 0)
                    q2 = region_data.get('q2', 0)
                    q3 = region_data.get('q3', 0)
                    q4 = region_data.get('q4', 0)
                    q5 = region_data.get('q5', 0)
                    
                    regions_sheet.append([
                        region.get('region_name', region.get('name', 'N/A')),
                        region.get('country_name', 'N/A'),
                        f"{regional_bonus:.2f}",
                        f"{region.get('pollution', 0):.2f}",
                        bonus_type,
                        f"{country_bonus:.2f}%",
                        f"{total_productivity:.2f}%",
                        f"{q1:.1f}",
                        f"{q2:.1f}",
                        f"{q3:.1f}",
                        f"{q4:.1f}",
                        f"{q5:.1f}"
                    ])
                
                sheets_data[f"Production Regions - {bonus_type}"] = regions_sheet
        
        # Sheet 8: Military Ranking
        military_summary = data.get('military_summary', {})
        if military_summary:
            military_data = [["Country", "Damage", "Position", "Status"]]
            sorted_military = sorted(military_summary.items(), key=lambda x: x[1], reverse=True)
            for i, (country, damage) in enumerate(sorted_military[:20], 1):
                military_data.append([
                    country,
                    f"{damage:,}",
                    i,
                    "Active" if damage > 0 else "Inactive"
                ])
            sheets_data["Military Ranking"] = military_data
        
        # Sheet 9: Top Warriors (moved to end)
        warriors_data = [["Position", "Name", "Country", "Level", "Points"]]
        top_warriors = data.get('top_warriors', [])
        
        for i, warrior in enumerate(top_warriors[:20], 1):  # Top 20
            country_name = "N/A"
            if 'nationality_id' in warrior:
                country_info = country_map.get(warrior['nationality_id'], {})
                if isinstance(country_info, dict):
                    country_name = country_info.get('name', 'N/A')
                else:
                    # Fallback: country_map might be simple {id: name} dict
                    country_name = str(country_info) if country_info else 'N/A'
            
            warriors_data.append([
                i,
                warrior.get('username', 'N/A'),
                country_name,
                warrior.get('level', 0),
                warrior.get('points', 0)
            ])
        
        sheets_data["Top Warriors"] = warriors_data
        
        return sheets_data
    
    def format_economic_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """Format economic report data for Google Sheets - ALWAYS ENHANCED VERSION"""
        
        # Zawsze używaj zaawansowanego formattera dla kompleksowej analizy ekonomicznej
        print("📊 Using enhanced comprehensive economic analysis...")
        
        from .enhanced_sheets_formatter import EnhancedSheetsFormatter
        enhanced_formatter = EnhancedSheetsFormatter()
        
        return enhanced_formatter.format_comprehensive_economic_report(data)
    
    def format_production_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """Format production report data for Google Sheets"""
        sheets_data = {}
        
        production_data = data.get('production_data', [])
        
        # Sheet 1: Regions Ranking
        ranking_data = [["Position", "Region", "Country", "Efficiency", "Pollution", "Bonus"]]
        
        for i, item in enumerate(production_data[:30], 1):  # Top 30
            ranking_data.append([
                i,
                item.get('region_name', 'N/A'),
                item.get('country_name', 'N/A'),
                item.get('efficiency_score', 0),
                item.get('pollution', 0),
                item.get('total_bonus', 0)
            ])
        
        sheets_data["Regions Ranking"] = ranking_data
        
        return sheets_data