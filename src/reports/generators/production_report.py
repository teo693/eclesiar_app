#!/usr/bin/env python3
"""
Refactored regional productivity analyzer for various goods in Eclesiar.
Now uses centralized calculation services to eliminate code duplication.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import sqlite3
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import os

from src.core.services.calculations import (
    ProductionCalculationService, 
    ProductionFactors, 
    ProductionResult,
    RegionCalculationService
)

# Legacy compatibility - keep ProductionData for existing code
@dataclass
class ProductionData:
    """Production data for a specific region and good - LEGACY"""
    region_name: str
    country_name: str
    country_id: int
    item_name: str  # good name
    total_bonus: float  # regional_bonus + country_bonus
    regional_bonus: float
    country_bonus: float
    bonus_type: str  # bonus type used for this product
    pollution: float
    npc_wages: float  # in GOLD
    production_q1: int
    production_q2: int
    production_q3: int
    production_q4: int
    production_q5: int
    efficiency_score: float  # score for sorting


class ProductionAnalyzer:
    """REFACTORED regional productivity analyzer using centralized services"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("ECLESIAR_DB_PATH", "eclesiar.db")
        
        # Initialize centralized calculation services
        self.production_calc = ProductionCalculationService(db_path)
        self.region_calc = RegionCalculationService()
        
        # Legacy compatibility - keep references for existing code
        self.npc_wages_cache = {}
        self.bonus_type_mapping = self.production_calc.bonus_type_mapping
        self.base_production = self.production_calc.base_production
    
    def load_npc_wages_data(self):
        """Loads real NPC wages data for all countries - REFACTORED to use centralized service"""
        # Delegate to centralized production calculation service
        self.production_calc.load_npc_wages_data()
        # Update legacy cache for backward compatibility
        self.npc_wages_cache = self.production_calc.npc_wages_cache
    
    def get_relevant_bonus(self, region_data: Dict[str, Any], item_name: str) -> Tuple[float, str]:
        """REFACTORED - Pobiera odpowiedni bonus używając centralnego serwisu"""
        return self.region_calc.get_regional_bonus_for_item(region_data, item_name)
    
    def _parse_bonus_description(self, bonus_description: str) -> Dict[str, float]:
        """REFACTORED - Deleguje do centralnego serwisu"""
        return self.region_calc._parse_bonus_description(bonus_description)
    
    def calculate_country_bonus(self, country_name: str, item_name: str) -> float:
        """REFACTORED - Deleguje do centralnego serwisu regionów używając bazy danych"""
        try:
            # Załaduj dane regionów z bazy używając DatabaseManagerService
            from src.core.services.database_manager_service import DatabaseManagerService
            db_manager = DatabaseManagerService(self.db_path)
            regions_data, summary = db_manager.get_regions_data()
            
            return self.region_calc.calculate_country_bonus(country_name, item_name, regions_data)
            
        except Exception as e:
            print(f"Error calculating country bonus for {country_name}: {e}")
            return 0.0
    
    def _get_bonus_type_for_item(self, item_name: str) -> str:
        """
        Mapuje nazwę towaru na typ bonusu w API.
        
        Args:
            item_name: Nazwa towaru
            
        Returns:
            Typ bonusu w API (np. "AIRCRAFT", "WEAPONS", "IRON")
        """
        item_mapping = {
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
        
        return item_mapping.get(item_name.lower(), None)
    
    def calculate_production_efficiency(self, region_data: Dict[str, Any], item_name: str, 
                                      company_tier: int = 5, eco_skill: int = 0, 
                                      workers_today: int = 0, is_npc_owned: bool = False,
                                      military_base_level: int = 0, production_field_level: int = 0,
                                      industrial_zone_level: int = 0, hospital_level: int = 0, 
                                      is_on_sale: bool = False) -> ProductionData:
        """
        REFACTORED - Oblicza efektywność produkcji używając centralnego serwisu
        """
        try:
            # Utwórz obiekt ProductionFactors z parametrów
            factors = ProductionFactors(
                company_tier=company_tier,
                eco_skill=eco_skill,
                workers_today=workers_today,
                is_npc_owned=is_npc_owned,
                military_base_level=military_base_level,
                production_field_level=production_field_level,
                industrial_zone_level=industrial_zone_level,
                hospital_level=hospital_level,
                is_on_sale=is_on_sale
            )
            
            # Deleguj obliczenia do centralnego serwisu
            result = self.production_calc.calculate_full_production(region_data, item_name, factors)
            
            if not result:
                return None
            
            # Konwertuj na legacy ProductionData dla kompatybilności
            return ProductionData(
                region_name=result.region_name,
                country_name=result.country_name,
                country_id=result.country_id,
                item_name=result.item_name,
                total_bonus=result.total_bonus,
                regional_bonus=result.regional_bonus,
                country_bonus=result.country_bonus,
                bonus_type=result.bonus_type,
                pollution=result.pollution,
                npc_wages=result.npc_wages,
                production_q1=result.production_q1,
                production_q2=result.production_q2,
                production_q3=result.production_q3,
                production_q4=result.production_q4,
                production_q5=result.production_q5,
                efficiency_score=result.efficiency_score
            )
            
        except Exception as e:
            print(f"Error calculating production efficiency: {e}")
            return None
    
    def analyze_all_regions(self, regions_data: List[Dict[str, Any]], 
                           default_company_tier: int = 5, default_eco_skill: int = 0,
                           default_workers_today: int = 0, default_is_npc_owned: bool = False,
                           default_military_base_level: int = 0, default_production_field_level: int = 0,
                           default_industrial_zone_level: int = 0, default_hospital_level: int = 0,
                           default_is_on_sale: bool = False) -> List[ProductionData]:
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
                    hospital_level=default_hospital_level,
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
                                 default_industrial_zone_level: int = 0, default_hospital_level: int = 0,
                                 default_is_on_sale: bool = False) -> str:
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
                default_hospital_level=default_hospital_level,
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
                    f.write(f"Total number of analyses: {len(production_data)}\n\n")
                    
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
        print("Missing production_config.py file - using default values")
        get_config = lambda x: {}
        print_available_scenarios = lambda: print("No available scenarios")
    
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
    print("TEST 1: Default configuration")
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
