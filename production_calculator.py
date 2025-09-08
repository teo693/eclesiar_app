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
from production_analyzer_consolidated import ProductionAnalyzer, ProductionData
from economy import fetch_countries_and_currencies, fetch_country_statistics
from api_client import fetch_data


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
    """Interactive regional productivity calculator"""
    
    def __init__(self):
        self.analyzer = ProductionAnalyzer()
        self.regions_data = []
        self.countries_data = {}
        self.items_list = []
        
        # List of available products
        self.available_items = [
            "grain", "iron", "titanium", "fuel",
            "food", "weapon", "aircraft", "airplane ticket"
        ]
        
        # List of company tiers
        self.company_tiers = [1, 2, 3, 4, 5]
        
        # List of building levels
        self.building_levels = [0, 1, 2, 3, 4, 5]
    
    def load_regions_data(self):
        """Loads region data from API"""
        try:
            print("🔄 Loading region data...")
            
            # Fetch country data
            countries, currencies, currency_codes, gold_id = fetch_countries_and_currencies()
            self.countries_data = countries
            
            # Fetch region data (sample data - in reality from API)
            # TODO: Implement fetching real region data
            self.regions_data = self._get_sample_regions_data()
            
            print(f"✅ Loaded {len(self.regions_data)} regions from {len(countries)} countries")
            
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
        
        while True:
            try:
                choice = input(f"\nSelect region (1-{len(self.regions_data)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(self.regions_data):
                    selected_region = self.regions_data[choice_num - 1]
                    print(f"✅ Selected: {selected_region['region_name']} ({selected_region['country_name']})")
                    return selected_region
                else:
                    print(f"❌ Select number from 1 to {len(self.regions_data)}")
                    
            except ValueError:
                print("❌ Enter a valid number")
    
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
                    print(f"❌ Wybierz liczbę od 1 do {len(self.company_tiers)}")
                    
            except ValueError:
                print("❌ Wprowadź poprawną liczbę")
        
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
                    print("❌ Eco Skill musi być między 0 a 100")
                    
            except ValueError:
                print("❌ Wprowadź poprawną liczbę")
        
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
                    print("❌ Liczba pracowników musi być między 0 a 100")
                    
            except ValueError:
                print("❌ Wprowadź poprawną liczbę")
        
        # Właściciel firmy
        while True:
            owner = input("\nCzy firma należy do NPC? (t/n): ").strip().lower()
            if owner in ['t', 'tak', 'y', 'yes']:
                params['is_npc_owned'] = True
                print("✅ Firma należy do NPC")
                break
            elif owner in ['n', 'nie', 'no']:
                params['is_npc_owned'] = False
                print("✅ Firma należy do gracza")
                break
            else:
                print("❌ Wprowadź 't' (tak) lub 'n' (nie)")
        
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
                    print("❌ Poziom Military Base musi być między 0 a 5")
                    
            except ValueError:
                print("❌ Wprowadź poprawną liczbę")
        
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
                    print("❌ Poziom budynku musi być między 0 a 5")
                    
            except ValueError:
                print("❌ Wprowadź poprawną liczbę")
        
        # Status firmy
        while True:
            sale = input("\nCzy firma jest na sprzedaż? (t/n): ").strip().lower()
            if sale in ['t', 'tak', 'y', 'yes']:
                params['is_on_sale'] = True
                print("✅ Firma jest na sprzedaż")
                break
            elif sale in ['n', 'nie', 'no']:
                params['is_on_sale'] = False
                print("✅ Firma nie jest na sprzedaż")
                break
            else:
                print("❌ Wprowadź 't' (tak) lub 'n' (nie)")
        
        return params
    
    def calculate_production(self, region: Dict[str, Any], item: str, params: Dict[str, Any]) -> ProductionData:
        """Oblicza produkcję dla wybranych parametrów"""
        try:
            # Załaduj dane NPC wages jeśli nie są załadowane
            if not self.analyzer.npc_wages_cache:
                self.analyzer.load_npc_wages_data()
            
            # Oblicz produkcję
            production_data = self.analyzer.calculate_production_efficiency(
                region, item,
                company_tier=params['company_tier'],
                eco_skill=params['eco_skill'],
                workers_today=params['workers_today'],
                is_npc_owned=params['is_npc_owned'],
                military_base_level=params['military_base_level'],
                production_field_level=params['production_field_level'],
                industrial_zone_level=params['industrial_zone_level'],
                is_on_sale=params['is_on_sale']
            )
            
            return production_data
            
        except Exception as e:
            print(f"❌ Błąd podczas obliczania: {e}")
            return None
    
    def display_results(self, production_data: ProductionData, params: Dict[str, Any]):
        """Wyświetla wyniki obliczeń"""
        if not production_data:
            print("❌ Nie udało się obliczyć produkcji")
            return
        
        print("\n" + "=" * 60)
        print("📊 WYNIKI OBLICZEŃ")
        print("=" * 60)
        
        # Podstawowe informacje
        print(f"📍 Region: {production_data.region_name} ({production_data.country_name})")
        print(f"📦 Produkt: {production_data.item_name.title()}")
        print(f"🏢 Poziom firmy: Q{params['company_tier']}")
        print(f"👥 Pracownicy: {params['workers_today']}")
        print(f"🎯 Eco Skill: {params['eco_skill']}")
        print(f"🏭 Poziom budynku: {params['production_field_level']}")
        print(f"🏛️ Military Base: {params['military_base_level']}")
        print(f"👤 Właściciel: {'NPC' if params['is_npc_owned'] else 'Gracz'}")
        print(f"💰 Status: {'Na sprzedaż' if params['is_on_sale'] else 'Aktywna'}")
        
        print("\n" + "-" * 60)
        print("📈 PRODUKCJA WEDŁUG JAKOŚCI")
        print("-" * 60)
        print(f"Q1: {production_data.production_q1:4d} jednostek")
        print(f"Q2: {production_data.production_q2:4d} jednostek")
        print(f"Q3: {production_data.production_q3:4d} jednostek")
        print(f"Q4: {production_data.production_q4:4d} jednostek")
        print(f"Q5: {production_data.production_q5:4d} jednostek")
        
        print("\n" + "-" * 60)
        print("📊 STATYSTYKI REGIONU")
        print("-" * 60)
        print(f"🎯 Efficiency Score: {production_data.efficiency_score:.2f}")
        print(f"📈 Bonus regionalny: {production_data.regional_bonus:.1%}")
        print(f"🏭 Typ bonusu: {production_data.bonus_type}")
        print(f"🌫️ Zanieczyszczenie: {production_data.pollution:.1f}%")
        print(f"💰 Płace NPC: {production_data.npc_wages:.2f} GOLD")
        
        # Analiza efektywności
        print("\n" + "-" * 60)
        print("💡 ANALIZA EFEKTYWNOŚCI")
        print("-" * 60)
        
        if production_data.efficiency_score > 100:
            print("🟢 Bardzo dobra efektywność!")
        elif production_data.efficiency_score > 80:
            print("🟡 Dobra efektywność")
        elif production_data.efficiency_score > 60:
            print("🟠 Średnia efektywność")
        else:
            print("🔴 Niska efektywność")
        
        # Rekomendacje
        print("\n💡 REKOMENDACJE:")
        if production_data.pollution > 10:
            print("   • Rozważ redukcję zanieczyszczenia")
        if production_data.npc_wages > 5:
            print("   • Wysokie płace NPC - rozważ inny region")
        if params['eco_skill'] < 20:
            print("   • Zwiększ Eco Skill dla lepszej produkcji")
        if params['workers_today'] == 0:
            print("   • Zatrudnij pracowników dla lepszej produkcji")
    
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
                print("\n\n👋 Dziękujemy za korzystanie z kalkulatora!")
                break
            except Exception as e:
                print(f"\n❌ Wystąpił błąd: {e}")
                continue
        
        print("\n👋 Dziękujemy za korzystanie z kalkulatora produktywności!")


def main():
    """Główna funkcja"""
    try:
        calculator = ProductionCalculator()
        calculator.run_calculator()
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
