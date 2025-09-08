#!/usr/bin/env python3
"""
Konsolidowany analizator produktywności regionów dla różnych towarów w Eclesiar.
Implementuje wszystkie 8 czynników wpływających na produkcję zgodnie z dokumentacją gry.

DANE DOSTĘPNE Z API:
✅ Bonusy regionalne (region bonus)
✅ Zanieczyszczenie (pollution)
✅ Płace NPC (npc wages)
✅ Lista towarów i krajów

DANE BRAKUJĄCE (używane domyślne wartości):
❌ Bazowe wartości produkcji Q1-Q5 (hardkodowane na podstawie dokumentacji)
❌ Poziomy military base (domyślnie 0)
❌ Poziomy Production Fields/Industrial Zones (domyślnie 0)
❌ Eco skill graczy (domyślnie 0)
❌ Liczba pracowników w firmach (domyślnie 0)
❌ Status firm (na sprzedaż) (domyślnie False)
❌ Właściciel firmy (NPC vs gracz) (domyślnie False)
❌ Bonusy krajowe (domyślnie 0)

UWAGA: Aby uzyskać dokładne obliczenia, należy dostarczyć brakujące dane
lub zaimplementować odpowiednie API endpoints.
"""

import sqlite3
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import os

from economy import fetch_country_statistics, fetch_countries_and_currencies, build_currency_rates_map


@dataclass
class ProductionData:
    """Dane o produkcji dla konkretnego regionu i towaru"""
    region_name: str
    country_name: str
    country_id: int
    item_name: str  # nazwa towaru
    total_bonus: float  # regional_bonus + country_bonus
    regional_bonus: float
    country_bonus: float
    bonus_type: str  # typ bonusu użytego dla tego produktu
    pollution: float
    npc_wages: float  # w GOLD
    production_q1: int
    production_q2: int
    production_q3: int
    production_q4: int
    production_q5: int
    efficiency_score: float  # score do sortowania


class ProductionAnalyzer:
    """Konsolidowany analizator produktywności regionów"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("ECLESIAR_DB_PATH", "eclesiar.db")
        self.npc_wages_cache = {}
        
        # Mapowanie typów bonusów na produkty (API używa wielkich liter)
        self.bonus_type_mapping = {
            # Surowce
            "grain": ["GRAIN", "grain", "food", "general"],
            "iron": ["IRON", "iron", "weapon", "aircraft", "general"],
            "titanium": ["TITANIUM", "titanium", "aircraft", "general"],
            "fuel": ["OIL", "fuel", "aircraft", "general"],
            
            # Produkty
            "food": ["FOOD", "food", "grain", "general"],
            "weapon": ["WEAPONS", "weapon", "iron", "general"],  # TICKETS removed - should not apply to weapon production
            "aircraft": ["AIRCRAFT", "aircraft", "titanium", "iron", "general"],
            "airplane ticket": ["TICKETS", "airplane ticket", "ticket", "aircraft", "general"]
        }
        
        # Bazowe wartości produkcji dla różnych towarów
        # Wartości z rzeczywistych danych gry (1 pracownik, eco skill 0)
        # Te wartości to bazowa produkcja bez eco skill bonus
        self.base_production = {
            # Surowce - używają Production Fields
            "grain": {
                "q1": 19, "q2": 29, "q3": 58, "q4": 78, "q5": 97,
                "building_type": "Production Field"
            },
            "iron": {
                "q1": 19, "q2": 29, "q3": 58, "q4": 78, "q5": 97,
                "building_type": "Production Field"
            },
            "titanium": {
                "q1": 19, "q2": 29, "q3": 58, "q4": 78, "q5": 97,
                "building_type": "Production Field"
            },
            "fuel": {
                "q1": 19, "q2": 29, "q3": 58, "q4": 78, "q5": 97,
                "building_type": "Production Field"
            },
            
            # Produkty - używają Industrial Zone
            "food": {
                "q1": 60, "q2": 49, "q3": 38, "q4": 27, "q5": 16,
                "building_type": "Industrial Zone"
            },
            "weapon": {
                "q1": 197, "q2": 143, "q3": 105, "q4": 77, "q5": 56,
                "building_type": "Industrial Zone"
            },
            "aircraft": {
                "q1": 90, "q2": 65, "q3": 47, "q4": 34, "q5": 25,
                "building_type": "Industrial Zone"
            },
            "airplane ticket": {
                "q1": 40, "q2": 29, "q3": 21, "q4": 15, "q5": 11,
                "building_type": "Industrial Zone"
            },
        }
    
    def load_npc_wages_data(self):
        """Ładuje rzeczywiste dane NPC wages dla wszystkich krajów"""
        try:
            print("Pobieranie rzeczywistych danych NPC wages...")
            
            # Pobierz dane o krajach i walutach
            eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
            
            if not eco_countries or not currencies_map:
                print("Błąd: Nie można pobrać danych o krajach i walutach")
                return
            
            # Pobierz kursy walut
            currency_rates = build_currency_rates_map(currencies_map, gold_id)
            
            # Pobierz dane o NPC wages
            npc_wage_raw = fetch_country_statistics("npcwage")
            
            # Sprawdź czy to jest słownik z kluczem 'data'
            if isinstance(npc_wage_raw, dict) and 'data' in npc_wage_raw:
                npc_wage_data = npc_wage_raw['data']
            else:
                npc_wage_data = npc_wage_raw
            
            # Utwórz słownik country_id -> wage_in_gold
            for country in npc_wage_data:
                # Sprawdź strukturę danych
                if "country" in country and "id" in country["country"]:
                    country_id = country["country"]["id"]
                else:
                    # Fallback: spróbuj bezpośrednio z country
                    country_id = country.get("id")
                
                local_wage = country.get("value", 0)
                
                if country_id and local_wage > 0:
                    # NPC wages z API są już w GOLD, nie trzeba przeliczać
                    self.npc_wages_cache[country_id] = local_wage
            
            print(f"Loaded NPC wages data for {len(self.npc_wages_cache)} countries")
            
        except Exception as e:
            print(f"Error loading NPC wages data: {e}")
            # Użyj domyślnych wartości
            self.npc_wages_cache = {}
    
    def get_relevant_bonus(self, region_data: Dict[str, Any], item_name: str) -> Tuple[float, str]:
        """
        Pobiera odpowiedni bonus dla konkretnego produktu z regionu.
        
        Args:
            region_data: Dane regionu z bonusami
            item_name: Nazwa produktu
            
        Returns:
            Krotka (bonus w procentach, typ bonusu)
        """
        bonus_by_type = region_data.get("bonus_by_type", {})
        
        # Jeśli bonus_by_type nie istnieje lub jest pusty, spróbuj sparsować bonus_description
        if not bonus_by_type:
            bonus_description = region_data.get("bonus_description", "")
            if bonus_description:
                # Parsuj bonus_description (format: "TICKETS:15" lub "WEAPONS:20 TICKETS:15")
                bonus_by_type = self._parse_bonus_description(bonus_description)
        
        # Jeśli nadal nie ma bonus_by_type, użyj starego systemu
        if not bonus_by_type:
            total_bonus = region_data.get("bonus_score", 0)
            return (total_bonus / 100.0 if total_bonus > 0 else 0.0), "general"
        
        relevant_bonus_types = self.bonus_type_mapping.get(item_name.lower(), ["general"])
        
        # Znajdź pierwszy pasujący bonus
        for bonus_type in relevant_bonus_types:
            if bonus_type in bonus_by_type:
                return bonus_by_type[bonus_type] / 100.0, bonus_type  # Konwersja z procentów
        
        # Jeśli nie znaleziono pasującego bonusu, zwróć 0%
        return 0.0, "none"
    
    def _parse_bonus_description(self, bonus_description: str) -> Dict[str, float]:
        """
        Parsuje bonus_description do słownika bonus_by_type.
        
        Args:
            bonus_description: String w formacie "TICKETS:15" lub "WEAPONS:20 TICKETS:15"
            
        Returns:
            Słownik z bonusami według typów
        """
        bonus_by_type = {}
        if not bonus_description:
            return bonus_by_type
        
        # Podziel na części (spacje)
        parts = bonus_description.strip().split()
        for part in parts:
            if ':' in part:
                try:
                    bonus_type, bonus_value = part.split(':', 1)
                    bonus_by_type[bonus_type] = float(bonus_value)
                except ValueError:
                    continue
        
        return bonus_by_type
    
    def calculate_production_efficiency(self, region_data: Dict[str, Any], item_name: str, 
                                      company_tier: int = 5, eco_skill: int = 0, 
                                      workers_today: int = 0, is_npc_owned: bool = False,
                                      military_base_level: int = 0, production_field_level: int = 0,
                                      industrial_zone_level: int = 0, is_on_sale: bool = False) -> ProductionData:
        """
        Oblicza efektywność produkcji dla konkretnego regionu i towaru
        zgodnie z mechanikami Eclesiar (8 czynników wpływających na produkcję)
        """
        try:
            # Pobierz bazową produkcję dla towaru
            item_config = self.base_production.get(item_name.lower())
            if not item_config:
                return None
            
            building_type = item_config["building_type"]
            
            # Pobierz bazową produkcję dla danego tieru
            tier_key = f"q{company_tier}"
            if tier_key not in item_config:
                tier_key = "q5"  # Fallback do Q5
            base_production = item_config[tier_key]
            
            # Pobierz dane regionu
            region_name = region_data.get("region_name", region_data.get("name", "Unknown"))
            country_id = region_data.get("country_id")
            country_name = region_data.get("country_name", "Unknown")
            pollution = region_data.get("pollution", 0)
            bonus_score = region_data.get("bonus_score", 0)
            
            # Pobierz NPC wages dla kraju
            npc_wages = self.npc_wages_cache.get(country_id, 5.0)
            
            # ===== OBLICZANIE PRODUKCJI ZGODNIE Z MECHANIKAMI ECLESIAR =====
            
            # 1. NPC Company Owner - produkcja dzielona przez 3 dla produktów
            production = base_production
            if is_npc_owned and building_type == "Industrial Zone":
                production = production / 3
            
            # 2. Military base bonus (5% dla broni i air-weapons)
            if military_base_level >= 3 and item_name.lower() in ["weapon", "aircraft"]:
                production = production * 1.05
            
            # 3. Consecutive workers debuff
            # [production] = [production] * (1.3 - ( [AMOUNT OF WORKERS] / 10 ))
            worker_debuff = 1.3 - (workers_today / 10)
            production = production * max(0.1, worker_debuff)  # Minimum 10% produkcji
            
            # 4. Eco skill bonus
            # Bazowe wartości to produkcja z eco skill 0 (zgodnie z dokumentacją)
            # Zastosuj eco skill bonus: production = base * (1 + eco_skill/50)
            eco_bonus = 1 + (eco_skill / 50)
            production = int(production * eco_bonus)
            
            # 5. Region and country bonus (tylko odpowiedni bonus dla produktu)
            regional_bonus, bonus_type = self.get_relevant_bonus(region_data, item_name)
            country_bonus = 0.0  # TODO: Implementować country bonus gdy będzie dostępny w API
            total_bonus = regional_bonus + country_bonus
            production = production + (production * total_bonus)
            
            # 6. Pollution debuff
            # [production] = [production] - (([production] - ([production]*0.1)) * [POLLUTION_VALUE])
            if pollution > 0:
                pollution_debuff = (production - (production * 0.1)) * (pollution / 100.0)
                production = production - pollution_debuff
            
            # 7. Production fields and industrial zones (5% per level)
            if building_type == "Production Field" and production_field_level > 0:
                production = production * (1 + (production_field_level * 0.05))
            elif building_type == "Industrial Zone" and industrial_zone_level > 0:
                production = production * (1 + (industrial_zone_level * 0.05))
            
            # 8. Company state (on sale)
            if is_on_sale:
                production = production / 2
            
            # Oblicz produkcję dla wszystkich jakości (używając proporcji)
            production_q1 = int(production * (item_config["q1"] / item_config[tier_key]))
            production_q2 = int(production * (item_config["q2"] / item_config[tier_key]))
            production_q3 = int(production * (item_config["q3"] / item_config[tier_key]))
            production_q4 = int(production * (item_config["q4"] / item_config[tier_key]))
            production_q5 = int(production * (item_config["q5"] / item_config[tier_key]))
            
            # Oblicz score efektywności (wyższy = lepszy)
            efficiency_score = (production_q5 * 5 + production_q4 * 4 + production_q3 * 3 + 
                              production_q2 * 2 + production_q1) / (5 + 4 + 3 + 2 + 1)
            
            # Normalizuj score względem kosztów operacyjnych
            if pollution > 0:
                efficiency_score = efficiency_score / (1 + pollution / 100.0)
            
            if npc_wages > 0:
                efficiency_score = efficiency_score / (1 + npc_wages / 10.0)
            
            return ProductionData(
                region_name=region_name,
                country_name=country_name,
                country_id=country_id,
                item_name=item_name,
                total_bonus=total_bonus,
                regional_bonus=regional_bonus,
                country_bonus=country_bonus,
                bonus_type=bonus_type,
                pollution=pollution,
                npc_wages=npc_wages,
                production_q1=production_q1,
                production_q2=production_q2,
                production_q3=production_q3,
                production_q4=production_q4,
                production_q5=production_q5,
                efficiency_score=efficiency_score
            )
            
        except Exception as e:
            print(f"Błąd podczas obliczania efektywności produkcji: {e}")
            return None
    
    def analyze_all_regions(self, regions_data: List[Dict[str, Any]], 
                           default_company_tier: int = 5, default_eco_skill: int = 0,
                           default_workers_today: int = 0, default_is_npc_owned: bool = False,
                           default_military_base_level: int = 0, default_production_field_level: int = 0,
                           default_industrial_zone_level: int = 0, default_is_on_sale: bool = False) -> List[ProductionData]:
        """
        Analizuje wszystkie regiony dla wszystkich towarów
        Używa domyślnych wartości dla parametrów, które nie są dostępne w API
        """
        if not regions_data:
            print("Brak danych o regionach do analizy")
            return []
        
        # Załaduj dane NPC wages jeśli nie są załadowane
        if not self.npc_wages_cache:
            self.load_npc_wages_data()
        
        all_production_data = []
        
        for region in regions_data:
            for item_name in self.base_production.keys():
                production_data = self.calculate_production_efficiency(
                    region, item_name,
                    company_tier=default_company_tier,
                    eco_skill=default_eco_skill,
                    workers_today=default_workers_today,
                    is_npc_owned=default_is_npc_owned,
                    military_base_level=default_military_base_level,
                    production_field_level=default_production_field_level,
                    industrial_zone_level=default_industrial_zone_level,
                    is_on_sale=default_is_on_sale
                )
                if production_data:
                    all_production_data.append(production_data)
        
        # Sortuj według score efektywności (malejąco)
        all_production_data.sort(key=lambda x: x.efficiency_score, reverse=True)
        
        return all_production_data
    
    def generate_production_report(self, regions_data: List[Dict[str, Any]], output_format: str = "txt",
                                 default_company_tier: int = 5, default_eco_skill: int = 0,
                                 default_workers_today: int = 0, default_is_npc_owned: bool = False,
                                 default_military_base_level: int = 0, default_production_field_level: int = 0,
                                 default_industrial_zone_level: int = 0, default_is_on_sale: bool = False) -> str:
        """Generuje raport produktywności"""
        try:
            production_data = self.analyze_all_regions(
                regions_data,
                default_company_tier=default_company_tier,
                default_eco_skill=default_eco_skill,
                default_workers_today=default_workers_today,
                default_is_npc_owned=default_is_npc_owned,
                default_military_base_level=default_military_base_level,
                default_production_field_level=default_production_field_level,
                default_industrial_zone_level=default_industrial_zone_level,
                default_is_on_sale=default_is_on_sale
            )
            
            if not production_data:
                return "Brak danych do wygenerowania raportu"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if output_format.lower() == "txt":
                filename = f"production_analysis_{timestamp}.txt"
                filepath = os.path.join("production_analysis", filename)
                
                # Utwórz katalog jeśli nie istnieje
                os.makedirs("production_analysis", exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("RAPORT PRODUKTYWNOŚCI REGIONÓW ECLESIAR\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Liczba analizowanych regionów: {len(regions_data)}\n")
                    f.write(f"Liczba analizowanych towarów: {len(self.base_production)}\n")
                    f.write(f"Łączna liczba analiz: {len(production_data)}\n\n")
                    
                    f.write("TOP 20 NAJLEPSZYCH REGIONÓW:\n")
                    f.write("-" * 30 + "\n")
                    
                    for i, data in enumerate(production_data[:20], 1):
                        f.write(f"{i:2d}. {data.region_name} ({data.country_name})\n")
                        f.write(f"     Score: {data.efficiency_score:.2f}\n")
                        f.write(f"     Bonus: {data.total_bonus:.2%}\n")
                        f.write(f"     Produkcja Q5: {data.production_q5}\n")
                        f.write(f"     Zanieczyszczenie: {data.pollution}\n")
                        f.write(f"     Płace NPC: {data.npc_wages:.2f} GOLD\n\n")
                
                return f"Raport wygenerowany: {filepath}"
            
            else:
                return f"Nieobsługiwany format: {output_format}"
                
        except Exception as e:
            return f"Błąd podczas generowania raportu: {e}"
    
    def get_top_regions(self, regions_data: List[Dict[str, Any]], limit: int = 10, **kwargs) -> List[ProductionData]:
        """Zwraca top N najlepszych regionów"""
        production_data = self.analyze_all_regions(regions_data, **kwargs)
        return production_data[:limit]
    
    def get_regions_by_country(self, regions_data: List[Dict[str, Any]], country_name: str, **kwargs) -> List[ProductionData]:
        """Zwraca regiony dla konkretnego kraju"""
        production_data = self.analyze_all_regions(regions_data, **kwargs)
        return [data for data in production_data if data.country_name.lower() == country_name.lower()]
    
    def get_regions_by_item(self, regions_data: List[Dict[str, Any]], item_name: str, **kwargs) -> List[ProductionData]:
        """Zwraca regiony dla konkretnego towaru"""
        production_data = self.analyze_all_regions(regions_data, **kwargs)
        return [data for data in production_data if data.item_name.lower() == item_name.lower()]


def main():
    """Główna funkcja do testowania"""
    try:
        from production_config import get_config, print_available_scenarios
    except ImportError:
        print("Brak pliku production_config.py - używam domyślnych wartości")
        get_config = lambda x: {}
        print_available_scenarios = lambda: print("Brak dostępnych scenariuszy")
    
    analyzer = ProductionAnalyzer()
    
    # Przykładowe dane regionów
    sample_regions = [
        {
            'region_name': 'Sample Region 1',
            'country_name': 'Sample Country',
            'country_id': 1,
            'bonus_score': 15.0,
            'pollution': 5.0
        },
        {
            'region_name': 'Sample Region 2',
            'country_name': 'Sample Country',
            'country_id': 1,
            'bonus_score': 20.0,
            'pollution': 3.0
        }
    ]
    
    print_available_scenarios()
    print("\n" + "="*50)
    print("TEST 1: Domyślna konfiguracja")
    print("="*50)
    
    # Test z domyślną konfiguracją
    config = get_config("default")
    report = analyzer.generate_production_report(sample_regions, **config)
    print(report)
    
    print("\n" + "="*50)
    print("TEST 2: Gracz z wysokim eco skill")
    print("="*50)
    
    # Test z wysokim eco skill
    config = get_config("high_eco")
    report = analyzer.generate_production_report(sample_regions, **config)
    print(report)


if __name__ == "__main__":
    main()
