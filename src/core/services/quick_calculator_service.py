#!/usr/bin/env python3
"""
Szybki kalkulator produktywności - wersja uproszczona
Pozwala szybko przetestować różne scenariusze bez interaktywnego interfejsu
"""

from src.reports.generators.production_report import ProductionAnalyzer


def quick_calculate(region_name: str, country_name: str, item_name: str, 
                   company_tier: int = 5, eco_skill: int = 16, 
                   workers_today: int = 0, is_npc_owned: bool = False,
                   military_base_level: int = 0, building_level: int = 0,
                   is_on_sale: bool = False):
    """
    Szybkie obliczenie produkcji dla podanych parametrów
    """
    
    # Spróbuj pobrać rzeczywiste dane z bazy
    from src.data.database.models import load_regions_data
    
    regions_data, summary = load_regions_data()
    region_data = None
    
    # Znajdź region w rzeczywistych danych
    for region in regions_data:
        if (region['region_name'].lower() == region_name.lower() and 
            region['country_name'].lower() == country_name.lower()):
            region_data = region
            break
    
    # Jeśli nie znaleziono, użyj domyślnych danych
    if not region_data:
        print(f"⚠️  Nie znaleziono regionu {region_name} ({country_name}) w bazie danych, używam domyślnych wartości")
        region_data = {
            'region_name': region_name,
            'country_name': country_name,
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
        }
    
    # Inicjalizuj analizator
    analyzer = ProductionAnalyzer()
    analyzer.load_npc_wages_data()
    
    # Oblicz produkcję
    production_data = analyzer.calculate_production_efficiency(
        region_data, item_name,
        company_tier=company_tier,
        eco_skill=eco_skill,
        workers_today=workers_today,
        is_npc_owned=is_npc_owned,
        military_base_level=military_base_level,
        production_field_level=building_level,
        industrial_zone_level=building_level,
        is_on_sale=is_on_sale
    )
    
    if production_data:
        print(f"📍 {region_name} ({country_name}) - {item_name.title()}")
        print(f"🏢 Q{company_tier} | 🎯 Eco: {eco_skill} | 👥 Workers: {workers_today}")
        print(f"🏭 Building: {building_level} | 🏛️ Military: {military_base_level}")
        print(f"👤 Owner: {'NPC' if is_npc_owned else 'Player'} | 💰 Sale: {'Yes' if is_on_sale else 'No'}")
        print("-" * 50)
        print(f"Q1: {production_data.production_q1:4d} | Q2: {production_data.production_q2:4d} | Q3: {production_data.production_q3:4d} | Q4: {production_data.production_q4:4d} | Q5: {production_data.production_q5:4d}")
        print(f"🎯 Score: {production_data.efficiency_score:.2f} | 📈 Bonus: {production_data.regional_bonus:.1%} | 🌫️ Pollution: {production_data.pollution:.1f}%")
        print()
    else:
        print(f"❌ Błąd obliczeń dla {region_name} - {item_name}")


def main():
    """Test różnych scenariuszy"""
    
    print("🚀 SZYBKI KALKULATOR PRODUKTYWNOŚCI")
    print("=" * 60)
    
    # Scenariusz 1: Podstawowy (eco skill 16)
    print("📊 SCENARIUSZ 1: Podstawowy (Eco Skill 16)")
    quick_calculate("Hurghada", "Slovenia", "weapon", 
                   company_tier=5, eco_skill=16, workers_today=0)
    
    # Scenariusz 2: Z pracownikami
    print("📊 SCENARIUSZ 2: Z pracownikami")
    quick_calculate("Hurghada", "Slovenia", "weapon", 
                   company_tier=5, eco_skill=16, workers_today=5)
    
    # Scenariusz 3: Wysoki eco skill
    print("📊 SCENARIUSZ 3: Wysoki Eco Skill")
    quick_calculate("Hurghada", "Slovenia", "weapon", 
                   company_tier=5, eco_skill=50, workers_today=0)
    
    # Scenariusz 4: Z budynkami
    print("📊 SCENARIUSZ 4: Z budynkami poziom 5")
    quick_calculate("Hurghada", "Slovenia", "weapon", 
                   company_tier=5, eco_skill=16, workers_today=0, building_level=5)
    
    # Scenariusz 5: NPC firma
    print("📊 SCENARIUSZ 5: NPC firma")
    quick_calculate("Hurghada", "Slovenia", "weapon", 
                   company_tier=5, eco_skill=16, workers_today=0, is_npc_owned=True)
    
    # Scenariusz 6: Różne produkty
    print("📊 SCENARIUSZ 6: Różne produkty")
    for item in ["weapon", "iron", "grain", "aircraft"]:
        quick_calculate("Hurghada", "Slovenia", item, 
                       company_tier=5, eco_skill=16, workers_today=0)
    
    # Scenariusz 7: Różne poziomy firm
    print("📊 SCENARIUSZ 7: Różne poziomy firm")
    for tier in [1, 3, 5]:
        quick_calculate("Hurghada", "Slovenia", "weapon", 
                       company_tier=tier, eco_skill=16, workers_today=0)


if __name__ == "__main__":
    main()

