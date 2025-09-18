#!/usr/bin/env python3
"""
Eclesiar Regional Productivity Calculator
Interactive calculator for calculating production in different regions
with the ability to select company parameters, workers and skills.
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from src.reports.generators.production_report import ProductionAnalyzer, ProductionData
from src.core.services.economy_service import fetch_countries_and_currencies, fetch_country_statistics
from src.data.api.client import fetch_data
from src.core.services.calculations import ProductionCalculationService, ProductionFactors


@dataclass
class CalculatorInput:
    """Input data for the calculator"""
    region_name: str
    country_name: str
    item_name: str
    company_tier: int
    eco_skill: int
    workers_today: int
    is_npc_owned: bool
    military_base_level: int
    production_field_level: int
    industrial_zone_level: int
    is_on_sale: bool


class ProductionCalculator:
    """REFACTORED Interactive regional productivity calculator using centralized services"""
    
    def __init__(self):
        # Initialize centralized calculation services
        self.production_calc = ProductionCalculationService()
        
        # Keep legacy analyzer for backward compatibility
        self.analyzer = ProductionAnalyzer()
        
        self.regions_data = []
        self.countries_data = {}
        self.items_list = []
        
        # List of available products - delegate to centralized service
        self.available_items = self.production_calc.get_available_items()
        
        # List of company tiers
        self.company_tiers = [1, 2, 3, 4, 5]
        
        # List of building levels
        self.building_levels = [0, 1, 2, 3, 4, 5]
    
    def load_regions_data(self):
        """Loads region data from database"""
        try:
            print("🔄 Loading region data...")
            
            # Fetch country data
            countries, currencies, currency_codes, gold_id = fetch_countries_and_currencies()
            self.countries_data = countries
            
            # Try to load real region data from database
            try:
                from src.data.database.models import load_regions_data
                self.regions_data, summary = load_regions_data()
                
                if self.regions_data:
                    print(f"✅ Loaded {len(self.regions_data)} regions from database")
                else:
                    print("⚠️ No regions in database, using sample data")
                    self.regions_data = self._get_sample_regions_data()
                    
            except Exception as db_error:
                print(f"⚠️ Database error: {db_error}, using sample data")
                self.regions_data = self._get_sample_regions_data()
            
            print(f"✅ Total regions available: {len(self.regions_data)}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.regions_data = self._get_sample_regions_data()
    
    def _get_sample_regions_data(self) -> List[Dict[str, Any]]:
        """Returns sample region data"""
        return [
            {
                'region_name': 'Hurghada',
                'country_name': 'Slovenia',
                'country_id': 1,
                'bonus_score': 0.0,
                'pollution': 0.0,
                'bonus_by_type': {
                    'GRAIN': 0.0,
                    'IRON': 0.0,
                    'WEAPONS': 0.0,
                    'AIRCRAFT': 0.0,
                    'FOOD': 0.0,
                    'TICKETS': 0.0
                }
            },
            {
                'region_name': 'Warsaw',
                'country_name': 'Poland',
                'country_id': 2,
                'bonus_score': 15.0,
                'pollution': 5.0,
                'bonus_by_type': {
                    'GRAIN': 10.0,
                    'IRON': 15.0,
                    'WEAPONS': 20.0,
                    'AIRCRAFT': 5.0,
                    'FOOD': 12.0,
                    'TICKETS': 0.0
                }
            },
            {
                'region_name': 'Berlin',
                'country_name': 'Germany',
                'country_id': 3,
                'bonus_score': 25.0,
                'pollution': 8.0,
                'bonus_by_type': {
                    'GRAIN': 5.0,
                    'IRON': 25.0,
                    'WEAPONS': 30.0,
                    'AIRCRAFT': 20.0,
                    'FOOD': 8.0,
                    'TICKETS': 0.0
                }
            }
        ]
    
    def display_welcome(self):
        """Wyświetla powitanie"""
        print("=" * 60)
        print("🏭 ECLESIAR REGIONAL PRODUCTIVITY CALCULATOR")
        print("=" * 60)
        print("Calculate optimal production for your region!")
        print()
    
    def select_region(self) -> Dict[str, Any]:
        """Pozwala użytkownikowi wybrać region"""
        print("📍 REGION SELECTION")
        print("-" * 30)
        
        if not self.regions_data:
            print("❌ No region data available")
            return None
        
        # Display available regions
        for i, region in enumerate(self.regions_data, 1):
            bonus = region.get('bonus_score', 0)
            pollution = region.get('pollution', 0)
            print(f"{i:2d}. {region['region_name']} ({region['country_name']})")
            print(f"     Bonus: {bonus:.1f}% | Pollution: {pollution:.1f}%")
        
        print(f"\n💡 You can:")
        print(f"   • Enter a number (1-{len(self.regions_data)}) to select from the list")
        print(f"   • Type region name directly (case insensitive)")
        print(f"   • Type 'q' to quit")
        
        while True:
            try:
                choice = input(f"\nSelect region: ").strip()
                
                # Check if user wants to quit
                if choice.lower() in ['q', 'quit', 'exit']:
                    return None
                
                # Try to parse as number first
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.regions_data):
                        selected_region = self.regions_data[choice_num - 1]
                        print(f"✅ Selected: {selected_region['region_name']} ({selected_region['country_name']})")
                        return selected_region
                    else:
                        print(f"❌ Select number from 1 to {len(self.regions_data)}")
                        continue
                except ValueError:
                    # Not a number, try to find by name
                    pass
                
                # Search for region by name (case insensitive)
                found_regions = []
                choice_lower = choice.lower()
                
                for region in self.regions_data:
                    region_name_lower = region['region_name'].lower()
                    country_name_lower = region['country_name'].lower()
                    
                    # Check if input matches region name or country name
                    if (choice_lower in region_name_lower or 
                        choice_lower in country_name_lower or
                        region_name_lower in choice_lower):
                        found_regions.append(region)
                
                if len(found_regions) == 1:
                    selected_region = found_regions[0]
                    print(f"✅ Found: {selected_region['region_name']} ({selected_region['country_name']})")
                    return selected_region
                elif len(found_regions) > 1:
                    print(f"🔍 Found {len(found_regions)} matching regions:")
                    for i, region in enumerate(found_regions, 1):
                        bonus = region.get('bonus_score', 0)
                        pollution = region.get('pollution', 0)
                        print(f"   {i}. {region['region_name']} ({region['country_name']}) - Bonus: {bonus:.1f}% | Pollution: {pollution:.1f}%")
                    
                    # Ask user to be more specific
                    while True:
                        try:
                            sub_choice = input(f"Select specific region (1-{len(found_regions)}): ").strip()
                            sub_choice_num = int(sub_choice)
                            if 1 <= sub_choice_num <= len(found_regions):
                                selected_region = found_regions[sub_choice_num - 1]
                                print(f"✅ Selected: {selected_region['region_name']} ({selected_region['country_name']})")
                                return selected_region
                            else:
                                print(f"❌ Select number from 1 to {len(found_regions)}")
                        except ValueError:
                            print("❌ Enter a valid number")
                else:
                    print(f"❌ No region found matching '{choice}'")
                    print("💡 Try typing part of the region name or country name")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return None
    
    def select_item(self) -> str:
        """Pozwala użytkownikowi wybrać produkt"""
        print("\n📦 PRODUCT SELECTION")
        print("-" * 30)
        
        for i, item in enumerate(self.available_items, 1):
            print(f"{i:2d}. {item.title()}")
        
        while True:
            try:
                choice = input(f"\nSelect product (1-{len(self.available_items)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(self.available_items):
                    selected_item = self.available_items[choice_num - 1]
                    print(f"✅ Selected: {selected_item.title()}")
                    return selected_item
                else:
                    print(f"❌ Select number from 1 to {len(self.available_items)}")
                    
            except ValueError:
                print("❌ Enter a valid number")
    
    def input_company_parameters(self) -> Dict[str, Any]:
        """Pozwala użytkownikowi wprowadzić parametry firmy"""
        print("\n🏢 COMPANY PARAMETERS")
        print("-" * 30)
        
        params = {}
        
        # Poziom firmy (Q1-Q5)
        print("Poziomy firmy:")
        for i, tier in enumerate(self.company_tiers, 1):
            print(f"{i}. Q{tier}")
        
        while True:
            try:
                choice = input(f"\nWybierz poziom firmy (1-{len(self.company_tiers)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(self.company_tiers):
                    params['company_tier'] = self.company_tiers[choice_num - 1]
                    print(f"✅ Wybrano: Q{params['company_tier']}")
                    break
                else:
                    print(f"❌ Choose a number from 1 to {len(self.company_tiers)}")
                    
            except ValueError:
                print("❌ Enter a valid number")
        
        # Eco skill
        while True:
            try:
                eco_skill = input("\nWprowadź poziom Eco Skill (0-100): ").strip()
                eco_skill_num = int(eco_skill)
                
                if 0 <= eco_skill_num <= 100:
                    params['eco_skill'] = eco_skill_num
                    print(f"✅ Eco Skill: {eco_skill_num}")
                    break
                else:
                    print("❌ Eco Skill must be between 0 and 100")
                    
            except ValueError:
                print("❌ Enter a valid number")
        
        # Liczba pracowników
        while True:
            try:
                workers = input("\nWprowadź liczbę pracowników (0-100): ").strip()
                workers_num = int(workers)
                
                if 0 <= workers_num <= 100:
                    params['workers_today'] = workers_num
                    print(f"✅ Pracownicy: {workers_num}")
                    break
                else:
                    print("❌ Number of workers must be between 0 and 100")
                    
            except ValueError:
                print("❌ Enter a valid number")
        
        # Właściciel firmy
        while True:
            owner = input("\nCzy firma należy do NPC? (t/n): ").strip().lower()
            if owner in ['t', 'tak', 'y', 'yes']:
                params['is_npc_owned'] = True
                print("✅ Company belongs to NPC")
                break
            elif owner in ['n', 'nie', 'no']:
                params['is_npc_owned'] = False
                print("✅ Company belongs to player")
                break
            else:
                print("❌ Enter 't' (yes) or 'n' (no)")
        
        # Poziom Military Base
        while True:
            try:
                military = input("\nWprowadź poziom Military Base (0-5): ").strip()
                military_num = int(military)
                
                if 0 <= military_num <= 5:
                    params['military_base_level'] = military_num
                    print(f"✅ Military Base: poziom {military_num}")
                    break
                else:
                    print("❌ Military Base level must be between 0 and 5")
                    
            except ValueError:
                print("❌ Enter a valid number")
        
        # Poziom budynków produkcyjnych
        while True:
            try:
                building = input("\nWprowadź poziom budynku produkcyjnego (0-5): ").strip()
                building_num = int(building)
                
                if 0 <= building_num <= 5:
                    params['production_field_level'] = building_num
                    params['industrial_zone_level'] = building_num
                    print(f"✅ Poziom budynku: {building_num}")
                    break
                else:
                    print("❌ Building level must be between 0 and 5")
                    
            except ValueError:
                print("❌ Enter a valid number")
        
        # Status firmy
        while True:
            sale = input("\nCzy firma jest na sprzedaż? (t/n): ").strip().lower()
            if sale in ['t', 'tak', 'y', 'yes']:
                params['is_on_sale'] = True
                print("✅ Company is for sale")
                break
            elif sale in ['n', 'nie', 'no']:
                params['is_on_sale'] = False
                print("✅ Company is not for sale")
                break
            else:
                print("❌ Enter 't' (yes) or 'n' (no)")
        
        return params
    
    def calculate_production(self, region: Dict[str, Any], item: str, params: Dict[str, Any]) -> ProductionData:
        """REFACTORED - Oblicza produkcję używając centralnego serwisu"""
        try:
            # Utwórz obiekt ProductionFactors z parametrów
            factors = ProductionFactors(
                company_tier=params['company_tier'],
                eco_skill=params['eco_skill'],
                workers_today=params['workers_today'],
                is_npc_owned=params['is_npc_owned'],
                military_base_level=params['military_base_level'],
                production_field_level=params['production_field_level'],
                industrial_zone_level=params['industrial_zone_level'],
                hospital_level=params.get('hospital_level', 0),
                is_on_sale=params['is_on_sale']
            )
            
            # Deleguj obliczenia do centralnego serwisu
            result = self.production_calc.calculate_full_production(region, item, factors)
            
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
            print(f"❌ Error during calculation: {e}")
            return None
    
    def display_results(self, production_data: ProductionData, params: Dict[str, Any]):
        """Displays calculation results"""
        if not production_data:
            print("❌ Failed to calculate production")
            return
        
        print("\n" + "=" * 60)
        print("📊 CALCULATION RESULTS")
        print("=" * 60)
        
        # Podstawowe informacje
        print(f"📍 Region: {production_data.region_name} ({production_data.country_name})")
        print(f"📦 Produkt: {production_data.item_name.title()}")
        print(f"🏢 Poziom firmy: Q{params['company_tier']}")
        print(f"👥 Pracownicy: {params['workers_today']}")
        print(f"🎯 Eco Skill: {params['eco_skill']}")
        print(f"🏭 Building level: {params['production_field_level']}")
        print(f"🏛️ Military Base: {params['military_base_level']}")
        print(f"👤 Owner: {'NPC' if params['is_npc_owned'] else 'Player'}")
        print(f"💰 Status: {'For sale' if params['is_on_sale'] else 'Active'}")
        
        print("\n" + "-" * 60)
        print("📈 PRODUCTION BY QUALITY")
        print("-" * 60)
        print(f"Q1: {production_data.production_q1:4d} units")
        print(f"Q2: {production_data.production_q2:4d} units")
        print(f"Q3: {production_data.production_q3:4d} units")
        print(f"Q4: {production_data.production_q4:4d} units")
        print(f"Q5: {production_data.production_q5:4d} units")
        
        print("\n" + "-" * 60)
        print("📊 REGION STATISTICS")
        print("-" * 60)
        print(f"🎯 Efficiency Score: {production_data.efficiency_score:.2f}")
        print(f"📈 Regional bonus: {production_data.regional_bonus:.1%}")
        print(f"🏭 Bonus type: {production_data.bonus_type}")
        print(f"🌫️ Pollution: {production_data.pollution:.1f}%")
        print(f"💰 NPC wages: {production_data.npc_wages:.2f} GOLD")
        
        # Analiza efektywności
        print("\n" + "-" * 60)
        print("💡 EFFICIENCY ANALYSIS")
        print("-" * 60)
        
        if production_data.efficiency_score > 100:
            print("🟢 Very good efficiency!")
        elif production_data.efficiency_score > 80:
            print("🟡 Good efficiency")
        elif production_data.efficiency_score > 60:
            print("🟠 Average efficiency")
        else:
            print("🔴 Low efficiency")
        
        # Rekomendacje
        print("\n💡 RECOMMENDATIONS:")
        if production_data.pollution > 10:
            print("   • Consider reducing pollution")
        if production_data.npc_wages > 5:
            print("   • High NPC wages - consider another region")
        if params['eco_skill'] < 20:
            print("   • Increase Eco Skill for better production")
        if params['workers_today'] == 0:
            print("   • Hire workers for better production")
    
    def run_calculator(self):
        """Uruchamia główną pętlę kalkulatora"""
        self.display_welcome()
        self.load_regions_data()
        
        while True:
            try:
                # Wybór regionu
                region = self.select_region()
                if not region:
                    break
                
                # Wybór produktu
                item = self.select_item()
                
                # Parametry firmy
                params = self.input_company_parameters()
                
                # Obliczenia
                print("\n🔄 Obliczanie produkcji...")
                production_data = self.calculate_production(region, item, params)
                
                # Wyniki
                self.display_results(production_data, params)
                
                # Kontynuacja
                print("\n" + "=" * 60)
                continue_choice = input("Czy chcesz obliczyć dla innego regionu? (t/n): ").strip().lower()
                if continue_choice not in ['t', 'tak', 'y', 'yes']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Thank you for using the calculator!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                continue
        
        print("\n👋 Thank you for using the productivity calculator!")


def main():
    """Główna funkcja"""
    try:
        calculator = ProductionCalculator()
        calculator.run_calculator()
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
