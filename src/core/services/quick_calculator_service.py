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
        print(f"⚠️  Region {region_name} ({country_name}) not found in database, using default values")
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
        print(f"🎯 Score: {production_data.efficiency_score:.2f} | 📈 Regional Bonus: {production_data.regional_bonus:.1%} | 🏛️ Country Bonus: {production_data.country_bonus:.1f}% | 🌫️ Pollution: {production_data.pollution:.1f}%")
        print()
    else:
        print(f"❌ Calculation error for {region_name} - {item_name}")


def interactive_quick_calculate():
    """Interactive quick calculator with region name input"""
    print("🚀 INTERACTIVE QUICK PRODUCTIVITY CALCULATOR")
    print("=" * 60)
    
    # Load regions data
    from src.data.database.models import load_regions_data
    regions_data, summary = load_regions_data()
    
    if not regions_data:
        print("❌ No region data available")
        return
    
    # Display available regions
    print("📍 Available regions:")
    for i, region in enumerate(regions_data[:10], 1):  # Show first 10 regions
        print(f"{i:2d}. {region['region_name']} ({region['country_name']})")
    
    if len(regions_data) > 10:
        print(f"   ... and {len(regions_data) - 10} more regions")
    
    print(f"\n💡 You can:")
    print(f"   • Enter a number (1-{min(10, len(regions_data))}) to select from the list")
    print(f"   • Type region name directly (case insensitive)")
    print(f"   • Type 'q' to quit")
    
    while True:
        try:
            choice = input(f"\nSelect region: ").strip()
            
            # Check if user wants to quit
            if choice.lower() in ['q', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            # Try to parse as number first
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= min(10, len(regions_data)):
                    selected_region = regions_data[choice_num - 1]
                    region_name = selected_region['region_name']
                    country_name = selected_region['country_name']
                    print(f"✅ Selected: {region_name} ({country_name})")
                else:
                    print(f"❌ Select number from 1 to {min(10, len(regions_data))}")
                    continue
            except ValueError:
                # Not a number, try to find by name
                found_regions = []
                choice_lower = choice.lower()
                
                for region in regions_data:
                    region_name_lower = region['region_name'].lower()
                    country_name_lower = region['country_name'].lower()
                    
                    # Check if input matches region name or country name
                    if (choice_lower in region_name_lower or 
                        choice_lower in country_name_lower or
                        region_name_lower in choice_lower):
                        found_regions.append(region)
                
                if len(found_regions) == 1:
                    selected_region = found_regions[0]
                    region_name = selected_region['region_name']
                    country_name = selected_region['country_name']
                    print(f"✅ Found: {region_name} ({country_name})")
                elif len(found_regions) > 1:
                    print(f"🔍 Found {len(found_regions)} matching regions:")
                    for i, region in enumerate(found_regions[:5], 1):  # Show max 5 matches
                        print(f"   {i}. {region['region_name']} ({region['country_name']})")
                    
                    if len(found_regions) > 5:
                        print(f"   ... and {len(found_regions) - 5} more matches")
                    
                    # Ask user to be more specific
                    while True:
                        try:
                            sub_choice = input(f"Select specific region (1-{min(5, len(found_regions))}): ").strip()
                            sub_choice_num = int(sub_choice)
                            if 1 <= sub_choice_num <= min(5, len(found_regions)):
                                selected_region = found_regions[sub_choice_num - 1]
                                region_name = selected_region['region_name']
                                country_name = selected_region['country_name']
                                print(f"✅ Selected: {region_name} ({country_name})")
                                break
                            else:
                                print(f"❌ Select number from 1 to {min(5, len(found_regions))}")
                        except ValueError:
                            print("❌ Enter a valid number")
                else:
                    print(f"❌ No region found matching '{choice}'")
                    print("💡 Try typing part of the region name or country name")
                    continue
            
            # Get product selection
            print("\n📦 Available products:")
            products = ["grain", "iron", "titanium", "fuel", "food", "weapon", "aircraft", "airplane ticket"]
            for i, product in enumerate(products, 1):
                print(f"{i:2d}. {product}")
            
            while True:
                try:
                    product_choice = input(f"\nSelect product (1-{len(products)}): ").strip()
                    product_num = int(product_choice)
                    if 1 <= product_num <= len(products):
                        item_name = products[product_num - 1]
                        print(f"✅ Selected: {item_name}")
                        break
                    else:
                        print(f"❌ Select number from 1 to {len(products)}")
                except ValueError:
                    print("❌ Enter a valid number")
            
            # Get company parameters
            print("\n🏢 Company Parameters:")
            try:
                company_tier = int(input("Company tier (1-5, default 5): ").strip() or "5")
                eco_skill = int(input("Eco skill (0-100, default 16): ").strip() or "16")
                workers_today = int(input("Workers today (0-100, default 0): ").strip() or "0")
                military_base_level = int(input("Military base level (0-5, default 0): ").strip() or "0")
                building_level = int(input("Building level (0-5, default 0): ").strip() or "0")
                
                is_npc_owned_input = input("NPC owned? (y/n, default n): ").strip().lower()
                is_npc_owned = is_npc_owned_input in ['y', 'yes', 't', 'tak']
                
                is_on_sale_input = input("On sale? (y/n, default n): ").strip().lower()
                is_on_sale = is_on_sale_input in ['y', 'yes', 't', 'tak']
                
            except ValueError:
                print("❌ Invalid input, using default values")
                company_tier, eco_skill, workers_today = 5, 16, 0
                military_base_level, building_level = 0, 0
                is_npc_owned, is_on_sale = False, False
            
            # Calculate production
            print(f"\n🔄 Calculating production for {region_name} ({country_name}) - {item_name}...")
            quick_calculate(region_name, country_name, item_name, 
                           company_tier=company_tier, eco_skill=eco_skill, 
                           workers_today=workers_today, is_npc_owned=is_npc_owned,
                           military_base_level=military_base_level, building_level=building_level,
                           is_on_sale=is_on_sale)
            
            # Ask if continue
            continue_choice = input("\n🔄 Calculate for another region? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', 't', 'tak']:
                break
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def main():
    """Test różnych scenariuszy"""
    
    print("🚀 QUICK PRODUCTIVITY CALCULATOR")
    print("=" * 60)
    print("Choose mode:")
    print("1. 📊 Run test scenarios (default)")
    print("2. 🎯 Interactive mode with region input")
    
    choice = input("\nSelect mode (1-2, default 1): ").strip() or "1"
    
    if choice == "2":
        interactive_quick_calculate()
        return
    
    # Original test scenarios
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
    print("📊 SCENARIO 6: Different products")
    for item in ["weapon", "iron", "grain", "aircraft"]:
        quick_calculate("Hurghada", "Slovenia", item, 
                       company_tier=5, eco_skill=16, workers_today=0)
    
    # Scenariusz 7: Różne poziomy firm
    print("📊 SCENARIO 7: Different company levels")
    for tier in [1, 3, 5]:
        quick_calculate("Hurghada", "Slovenia", "weapon", 
                       company_tier=tier, eco_skill=16, workers_today=0)


if __name__ == "__main__":
    main()

