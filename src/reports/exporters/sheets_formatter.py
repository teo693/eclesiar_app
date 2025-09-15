"""
Google Sheets Data Formatter

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json

class SheetsFormatter:
    """Formats data for Google Sheets export"""
    
    def __init__(self):
        self.date_format = "%Y-%m-%d %H:%M:%S"
        # Mapowanie typów bonusów dla produktów
        self.bonus_type_mapping = {
            "aircraft": "AIRCRAFT",
            "air-weapon": "AIRCRAFT", 
            "samolot": "AIRCRAFT",
            "weapon": "WEAPONS",
            "broń": "WEAPONS",
            "iron": "IRON",
            "grain": "GRAIN",
            "zboże": "GRAIN",
            "food": "FOOD",
            "fuel": "FUEL",
            "paliwo": "FUEL",
            "titanium": "TITANIUM",
            "tytan": "TITANIUM",
            "airplane ticket": "TICKETS",
            "bilet lotniczy": "TICKETS"
        }
    
    def calculate_country_bonus(self, country_name: str, regions_data: List[Dict[str, Any]], item_name: str = "grain") -> float:
        """
        Oblicza bonus krajowy na podstawie wzoru:
        suma bonusów regionalnych danego typu w kraju / 5 = bonus krajowy w %
        
        Args:
            country_name: Nazwa kraju
            regions_data: Lista regionów z bazy danych
            item_name: Nazwa towaru (domyślnie "grain")
            
        Returns:
            Bonus krajowy w procentach (jako float, np. 7.0 dla 7%)
        """
        try:
            # Znajdź wszystkie unikalne regiony w danym kraju (bez duplikatów)
            unique_regions = {}
            for region in regions_data:
                if region.get('country_name', '').lower() == country_name.lower():
                    region_key = region.get('region_name', region.get('name', '')).lower()
                    # Zachowaj tylko pierwszy (najnowszy) region o tej nazwie
                    if region_key not in unique_regions:
                        unique_regions[region_key] = region
            
            country_regions = list(unique_regions.values())
            
            if not country_regions:
                return 0.0
            
            # Określ typ bonusu dla danego towaru
            bonus_type = self.bonus_type_mapping.get(item_name.lower(), "GRAIN")
            
            # Zsumuj bonusy danego typu ze wszystkich unikalnych regionów w kraju
            total_bonus = 0.0
            regions_with_bonus = 0
            
            for region in country_regions:
                # Parsuj bonus_description do bonus_by_type
                bonus_description = region.get('bonus_description', '')
                if bonus_description:
                    bonus_by_type = self._parse_bonus_description(bonus_description)
                    if bonus_type in bonus_by_type:
                        bonus_value = bonus_by_type[bonus_type]
                        if bonus_value > 0:
                            total_bonus += bonus_value
                            regions_with_bonus += 1
            
            # Oblicz bonus krajowy: suma / 5
            if regions_with_bonus > 0:
                country_bonus = total_bonus / 5.0
                return country_bonus
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating country bonus for {country_name}: {e}")
            return 0.0
    
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
        """
        Pobiera bonus regionalny dla konkretnego typu towaru.
        
        Args:
            region: Dane regionu
            item_name: Nazwa towaru
            
        Returns:
            Bonus regionalny dla danego typu towaru
        """
        try:
            bonus_description = region.get('bonus_description', '')
            if not bonus_description:
                return 0.0
            
            bonus_by_type = self._parse_bonus_description(bonus_description)
            bonus_type = self.bonus_type_mapping.get(item_name.lower(), "GRAIN")
            
            result = bonus_by_type.get(bonus_type, 0.0)
            
            # Debug: sprawdź czy result jest liczbą
            if not isinstance(result, (int, float)):
                print(f"Warning: bonus result is not a number: {result} (type: {type(result)})")
                return 0.0
                
            return float(result)
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
            top_regions = sorted(regions, key=lambda x: x.get('bonus_score', 0), reverse=True)[:5]
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
            from datetime import datetime, timedelta
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
            sorted_rates = sorted(currency_rates.items(), key=lambda x: currencies_map.get(str(x[0]), f'Currency {x[0]}'))
            
            for currency_id, rate in sorted_rates:
                currency_name = currencies_map.get(str(currency_id), f'Currency {currency_id}')
                
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
                    f"{job.get('salary_gold', 0):.2f}",
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
                        print(f"Warning: total_productivity is not a number: {total_productivity} (type: {type(total_productivity)})")
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
                sorted_regions = sorted(regions_with_productivity, key=lambda x: x.get('total_productivity', 0) if isinstance(x, dict) else 0, reverse=True)
                
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
                        print(f"Warning: total_productivity is not a number: {total_productivity} (type: {type(total_productivity)})")
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
                sorted_regions = sorted(regions_with_productivity, key=lambda x: x.get('total_productivity', 0) if isinstance(x, dict) else 0, reverse=True)
                
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
        """Format economic report data for Google Sheets with only 2 main tabs"""
        sheets_data = {}
        
        # Sheet 1: Cheapest items - all products in one sheet
        cheapest_items = data.get('cheapest_items', {})
        items_map = data.get('items', {})
        
        # Mapowanie ID towarów na nazwy
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
        
        cheapest_sheet = []
        
        if cheapest_items:
            # Grupuj towary według typu (Grain, Food, Iron, Weapon, Fuel, Tickets, Titanium, Aircraft)
            product_groups = {
                "Grain": [],
                "Food": [],
                "Iron": [],
                "Weapon": [],
                "Fuel": [],
                "Tickets": [],
                "Titanium": [],
                "Aircraft": []
            }
            
            for item_id, items_list in cheapest_items.items():
                if items_list:
                    # Znajdź najtańszy przedmiot tego typu
                    cheapest_item = min(items_list, key=lambda x: x.get('price_gold', float('inf')))
                    item_name = item_names.get(item_id, f"Item {item_id}")
                    country = cheapest_item.get('country', 'N/A')
                    price = cheapest_item.get('price_gold', 0)
                    currency = cheapest_item.get('currency_name', 'N/A')
                    amount = cheapest_item.get('amount', 0)
                    avg5 = cheapest_item.get('avg5_in_gold', 0)
                    price_original = cheapest_item.get('price_currency', cheapest_item.get('price_in_currency', 0))
                    
                    # Określ grupę produktu
                    if "Grain" in item_name:
                        product_groups["Grain"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Food" in item_name:
                        product_groups["Food"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Iron" in item_name:
                        product_groups["Iron"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Weapon" in item_name:
                        product_groups["Weapon"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Fuel" in item_name:
                        product_groups["Fuel"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Tickets" in item_name:
                        product_groups["Tickets"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Titanium" in item_name:
                        product_groups["Titanium"].append((item_name, price, country, currency, amount, avg5, price_original))
                    elif "Aircraft" in item_name:
                        product_groups["Aircraft"].append((item_name, price, country, currency, amount, avg5, price_original))
            
            # Twórz arkusz z tabelami dla każdego typu produktu
            for product_type, items in product_groups.items():
                if items:
                    # Header for this product type
                    cheapest_sheet.append([f"🛒 {product_type.upper()}", "", "", "", "", "", ""])
                    cheapest_sheet.append(["Product", "Price (GOLD)", "Country", "Currency", "Original Price", "Amount", "5-day Average"])
                    
                    # Sortuj według ceny (najtańsze pierwsze)
                    items.sort(key=lambda x: x[1])
                    
                    # Add data rows
                    for item_name, price, country, currency, amount, avg5, price_original in items:
                        cheapest_sheet.append([
                            item_name,
                            f"{price:.6f}",
                            country,
                            currency,
                            f"{price_original:.2f}",
                            f"{amount}",
                            f"{avg5:.6f}"
                        ])
                    
                    # Add empty row between groups
                    cheapest_sheet.append(["", "", "", "", "", "", ""])
        
        sheets_data["Cheapest Items"] = cheapest_sheet
        
        # Sheet 2: Currency Rates with growth indicators
        currency_rates = data.get('currency_rates', {})
        currencies_map = data.get('currencies_map', {})
        historical_data = data.get('historical_data', {})
        
        if currency_rates:
            rates_data = [["Currency", "Rate vs GOLD", "Previous Rate", "Change %"]]
            
            # Pobierz wczorajsze kursy z danych historycznych
            from datetime import datetime, timedelta
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
            sorted_rates = sorted(currency_rates.items(), key=lambda x: currencies_map.get(str(x[0]), f'Currency {x[0]}'))
            
            for currency_id, rate in sorted_rates:
                currency_name = currencies_map.get(str(currency_id), f'Currency {currency_id}')
                
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
        
        # Sheet 3: Production Regions - all products in one sheet
        regions_data = data.get('regions', [])
        if not regions_data:
            # Fallback to regions if regions_data is not available
            raw_regions = data.get('regions', [])
            if raw_regions:
                # Process raw regions data to get proper country names
                from src.core.services.regions_service import process_regions_data
                countries_data = data.get('country_map', {})
                regions_data = process_regions_data(raw_regions, countries_data)
        
        regions_sheet = []
        
        if regions_data:
            # Import ProductionAnalyzer to analyze regions like in short economic report
            from src.reports.generators.production_report import ProductionAnalyzer
            
            # Analyze productivity
            analyzer = ProductionAnalyzer()
            production_data = analyzer.analyze_all_regions(regions_data)
            
            if production_data:
                # Group by product type
                products_groups = {}
                for data_item in production_data:
                    if hasattr(data_item, 'item_name'):
                        item_name = data_item.item_name
                    elif isinstance(data_item, dict):
                        item_name = data_item.get('item_name', 'Unknown')
                    else:
                        item_name = 'Unknown'
                    
                    if item_name not in products_groups:
                        products_groups[item_name] = []
                    products_groups[item_name].append(data_item)
                
                # Create tables for each product type in one sheet
                for product_name, items in products_groups.items():
                    if items:
                        # Sort by efficiency_score
                        items.sort(
                            key=lambda x: getattr(x, 'efficiency_score', 0) if hasattr(x, 'efficiency_score') else x.get('efficiency_score', 0) if isinstance(x, dict) else 0, 
                            reverse=True
                        )
                        
                        # Header for this product type
                        regions_sheet.append([f"🏭 PRODUCTION {product_name.upper()}", "", "", "", "", "", "", "", "", ""])
                        regions_sheet.append(["Region", "Country", "Score", "Regional Bonus", "Country Bonus", "Q1", "Q2", "Q3", "Q4", "Q5"])
                        
                        # Show top 10 regions for each product
                        for item in items[:10]:
                            # Data row - handle both object attributes and dictionary keys
                            if hasattr(item, 'region_name'):
                                # ProductionData object
                                regions_sheet.append([
                                    getattr(item, 'region_name', 'Unknown'),
                                    getattr(item, 'country_name', 'Unknown'),
                                    f"{getattr(item, 'efficiency_score', 0):.2f}",
                                    f"{getattr(item, 'regional_bonus', 0):.1%}",
                                    f"{getattr(item, 'country_bonus', 0):.1f}%",
                                    str(getattr(item, 'production_q1', 0)),
                                    str(getattr(item, 'production_q2', 0)),
                                    str(getattr(item, 'production_q3', 0)),
                                    str(getattr(item, 'production_q4', 0)),
                                    str(getattr(item, 'production_q5', 0))
                                ])
                            else:
                                # Dictionary
                                regions_sheet.append([
                                    item.get('region_name', 'Unknown'),
                                    item.get('country_name', 'Unknown'),
                                    f"{item.get('efficiency_score', 0):.2f}",
                                    f"{item.get('regional_bonus', 0):.1%}",
                                    f"{item.get('country_bonus', 0):.1f}%",
                                    str(item.get('production_q1', 0)),
                                    str(item.get('production_q2', 0)),
                                    str(item.get('production_q3', 0)),
                                    str(item.get('production_q4', 0)),
                                    str(item.get('production_q5', 0))
                                ])
                        
                        # Dodaj pusty wiersz między grupami
                        regions_sheet.append(["", "", "", "", "", "", "", "", "", ""])
            else:
                # Fallback to basic region data if production analysis fails
                regions_sheet.append(["Region", "Country", "Bonus", "Pollution", "Bonus Type"])
                for region in regions_data[:max(10, len(regions_data))]:  # Minimum 10, maksimum wszystkie dostępne
                    if isinstance(region, dict):
                        regions_sheet.append([
                            region.get('region_name', region.get('name', 'N/A')),
                            region.get('country_name', 'N/A'),
                            f"{region.get('bonus_score', 0):.2f}",
                            f"{region.get('pollution', 0):.2f}",
                            region.get('bonus_description', 'N/A')
                        ])
                    else:
                        # If region is not a dict, skip it
                        continue
        
        sheets_data["Production Regions"] = regions_sheet
        
        return sheets_data
    
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
