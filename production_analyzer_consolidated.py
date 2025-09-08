#!/usr/bin/env python3
"""
Konsolidowany analizator produktywności regionów dla różnych towarów w Eclesiar.
Łączy najlepsze funkcje z wszystkich wersji.
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
        
        # Bazowe wartości produkcji dla różnych towarów
        self.base_production = {
            # Surowce - używają Production Fields
            "grain": {"base": 80, "building_type": "Production Field"},
            "iron": {"base": 120, "building_type": "Production Field"},
            "titanium": {"base": 180, "building_type": "Production Field"},
            "fuel": {"base": 100, "building_type": "Production Field"},
            
            # Produkty - używają Industrial Zone
            "food": {"base": 60, "building_type": "Industrial Zone"},
            "weapon": {"base": 90, "building_type": "Industrial Zone"},
            "aircraft": {"base": 120, "building_type": "Industrial Zone"},
            "airplane ticket": {"base": 50, "building_type": "Industrial Zone"},
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
                    # Znajdź informacje o walucie tego kraju
                    country_info = eco_countries.get(country_id, {})
                    currency_id = country_info.get("currency_id")
                    
                    # Przelicz na gold
                    wage_in_gold = 5.0  # Domyślna wartość
                    
                    if currency_id and currency_id in currency_rates:
                        try:
                            # Przelicz wage z lokalnej waluty na gold
                            wage_in_gold = local_wage / currency_rates[currency_id]
                        except (ZeroDivisionError, TypeError):
                            wage_in_gold = 5.0  # Fallback
                    
                    self.npc_wages_cache[country_id] = wage_in_gold
            
            print(f"Załadowano dane NPC wages dla {len(self.npc_wages_cache)} krajów")
            
        except Exception as e:
            print(f"Błąd podczas ładowania danych NPC wages: {e}")
            # Użyj domyślnych wartości
            self.npc_wages_cache = {}
    
    def calculate_production_efficiency(self, region_data: Dict[str, Any], item_name: str) -> ProductionData:
        """Oblicza efektywność produkcji dla konkretnego regionu i towaru"""
        try:
            # Pobierz bazową produkcję dla towaru
            item_config = self.base_production.get(item_name.lower())
            if not item_config:
                return None
            
            base_production = item_config["base"]
            building_type = item_config["building_type"]
            
            # Pobierz dane regionu
            region_name = region_data.get("region_name", region_data.get("name", "Unknown"))
            country_id = region_data.get("country_id")
            country_name = region_data.get("country_name", "Unknown")
            pollution = region_data.get("pollution", 0)
            bonus_score = region_data.get("bonus_score", 0)
            
            # Pobierz NPC wages dla kraju
            npc_wages = self.npc_wages_cache.get(country_id, 5.0)
            
            # Oblicz bonusy
            regional_bonus = bonus_score / 100.0  # Konwersja z procentów
            country_bonus = 0.0  # Można dodać bonusy krajowe w przyszłości
            total_bonus = regional_bonus + country_bonus
            
            # Oblicz produkcję dla różnych jakości
            production_q1 = int(base_production * (1 + total_bonus))
            production_q2 = int(base_production * 1.2 * (1 + total_bonus))
            production_q3 = int(base_production * 1.5 * (1 + total_bonus))
            production_q4 = int(base_production * 2.0 * (1 + total_bonus))
            production_q5 = int(base_production * 3.0 * (1 + total_bonus))
            
            # Oblicz score efektywności (wyższy = lepszy)
            efficiency_score = (production_q5 * 5 + production_q4 * 4 + production_q3 * 3 + 
                              production_q2 * 2 + production_q1) / (5 + 4 + 3 + 2 + 1)
            
            # Normalizuj score względem zanieczyszczenia i płac NPC
            if pollution > 0:
                efficiency_score = efficiency_score / (1 + pollution / 1000.0)
            
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
    
    def analyze_all_regions(self, regions_data: List[Dict[str, Any]]) -> List[ProductionData]:
        """Analizuje wszystkie regiony dla wszystkich towarów"""
        if not regions_data:
            print("Brak danych o regionach do analizy")
            return []
        
        # Załaduj dane NPC wages jeśli nie są załadowane
        if not self.npc_wages_cache:
            self.load_npc_wages_data()
        
        all_production_data = []
        
        for region in regions_data:
            for item_name in self.base_production.keys():
                production_data = self.calculate_production_efficiency(region, item_name)
                if production_data:
                    all_production_data.append(production_data)
        
        # Sortuj według score efektywności (malejąco)
        all_production_data.sort(key=lambda x: x.efficiency_score, reverse=True)
        
        return all_production_data
    
    def generate_production_report(self, regions_data: List[Dict[str, Any]], output_format: str = "txt") -> str:
        """Generuje raport produktywności"""
        try:
            production_data = self.analyze_all_regions(regions_data)
            
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
    
    def get_top_regions(self, regions_data: List[Dict[str, Any]], limit: int = 10) -> List[ProductionData]:
        """Zwraca top N najlepszych regionów"""
        production_data = self.analyze_all_regions(regions_data)
        return production_data[:limit]
    
    def get_regions_by_country(self, regions_data: List[Dict[str, Any]], country_name: str) -> List[ProductionData]:
        """Zwraca regiony dla konkretnego kraju"""
        production_data = self.analyze_all_regions(regions_data)
        return [data for data in production_data if data.country_name.lower() == country_name.lower()]
    
    def get_regions_by_item(self, regions_data: List[Dict[str, Any]], item_name: str) -> List[ProductionData]:
        """Zwraca regiony dla konkretnego towaru"""
        production_data = self.analyze_all_regions(regions_data)
        return [data for data in production_data if item_name.lower() in data.region_name.lower()]


def main():
    """Główna funkcja do testowania"""
    analyzer = ProductionAnalyzer()
    
    # Przykładowe dane regionów
    sample_regions = [
        {
            'name': 'Sample Region 1',
            'country_name': 'Sample Country',
            'country_id': 1,
            'production_bonus': 15.0,
            'country_production_bonus': 10.0,
            'pollution': 5.0
        },
        {
            'name': 'Sample Region 2',
            'country_name': 'Sample Country',
            'country_id': 1,
            'production_bonus': 20.0,
            'country_production_bonus': 15.0,
            'pollution': 3.0
        }
    ]
    
    report = analyzer.generate_production_report(sample_regions)
    print(report)


if __name__ == "__main__":
    main()
