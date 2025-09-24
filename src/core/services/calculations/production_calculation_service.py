"""
Production Calculation Service

Centralny serwis do wszystkich obliczeń produktywności.
Implementuje wszystkie 8+ czynników wpływających na produkcję zgodnie z mechanikami Eclesiar.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import os

from src.core.services.economy_service import fetch_countries_and_currencies, fetch_country_statistics, build_currency_rates_map


@dataclass
class ProductionResult:
    """Wynik obliczeń produkcji"""
    region_name: str
    country_name: str
    country_id: int
    item_name: str
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
    building_type: str
    applied_factors: Dict[str, Any]  # Debug info about applied factors


@dataclass
class ProductionFactors:
    """Wszystkie czynniki wpływające na produkcję"""
    company_tier: int = 5
    eco_skill: int = 0
    workers_today: int = 0
    is_npc_owned: bool = False
    military_base_level: int = 0
    production_field_level: int = 0
    industrial_zone_level: int = 0
    hospital_level: int = 0
    is_on_sale: bool = False


class ProductionCalculationService:
    """Centralny serwis do wszystkich obliczeń produktywności"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("ECLESIAR_DB_PATH", "eclesiar.db")
        self.npc_wages_cache = {}
        
        # Mapping bonus types to products (API uses uppercase)
        self.bonus_type_mapping = {
            # Surowce
            "grain": ["GRAIN", "grain", "food", "general"],
            "iron": ["IRON", "iron", "weapon", "aircraft", "general"],
            "titanium": ["TITANIUM", "titanium", "aircraft", "general"],
            "fuel": ["OIL", "FUEL", "fuel", "aircraft", "general"],  # ✅ FIX: Add FUEL mapping
            "oil": ["OIL", "FUEL", "fuel", "aircraft", "general"],   # ✅ FIX: Add oil mapping
            
            # Produkty
            "food": ["FOOD", "food", "grain", "general"],
            "weapon": ["WEAPONS", "weapon", "iron", "general"],
            "aircraft": ["AIRCRAFT", "aircraft", "titanium", "iron", "general"],
            "airplane ticket": ["TICKETS", "airplane ticket", "ticket", "aircraft", "general"]
        }
        
        # Base production values for different goods
        # Values from real game data (1 worker, eco skill 0)
        self.base_production = {
            # Raw materials - use Production Fields
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
            
            # Products - use Industrial Zone
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
        """Loads real NPC wages data from database (DB-first approach)"""
        try:
            print("Loading NPC wages data from database...")
            
            # Ładuj dane z bazy danych zamiast z API
            from src.core.services.database_manager_service import DatabaseManagerService
            db_manager = DatabaseManagerService(self.db_path)
            
            # Pobierz oferty pracy z bazy danych (NPC wages są najmniejszymi wynagrodzeniami)
            job_offers = db_manager.get_job_offers()
            
            if not job_offers:
                print("⚠️ No job offers in database, falling back to API...")
                self._load_npc_wages_from_api()
                return
            
            # Znajdź najniższe wynagrodzenie w każdym kraju (to będzie NPC wage)
            country_wages = {}
            for job in job_offers:
                country_id = job.get('country_id')
                wage_gold = job.get('wage_gold', 0)
                
                if country_id and wage_gold > 0:
                    if country_id not in country_wages:
                        country_wages[country_id] = wage_gold
                    else:
                        # Znajdź minimum (NPC wage)
                        country_wages[country_id] = min(country_wages[country_id], wage_gold)
            
            self.npc_wages_cache = country_wages
            print(f"✅ Loaded NPC wages for {len(self.npc_wages_cache)} countries from database")
            
        except Exception as e:
            print(f"❌ Error loading NPC wages from database: {e}")
            print("🔄 Falling back to API...")
            self._load_npc_wages_from_api()
    
    def _load_npc_wages_from_api(self):
        """Fallback method to load NPC wages from API"""
        try:
            # Pobierz dane o krajach i walutach
            eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
            
            if not eco_countries or not currencies_map:
                print("Error: Cannot fetch countries and currencies data")
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
            
            print(f"✅ Loaded NPC wages for {len(self.npc_wages_cache)} countries from API")
            
        except Exception as e:
            print(f"❌ Error loading NPC wages from API: {e}")
    
    def calculate_base_production(self, item_name: str, company_tier: int) -> Optional[int]:
        """Oblicza bazową produkcję dla towaru i poziomu firmy"""
        item_config = self.base_production.get(item_name.lower())
        if not item_config:
            return None
        
        tier_key = f"q{company_tier}"
        if tier_key not in item_config:
            tier_key = "q5"  # Fallback do Q5
        
        return item_config[tier_key]
    
    def get_building_type(self, item_name: str) -> Optional[str]:
        """Zwraca typ budynku dla danego towaru"""
        item_config = self.base_production.get(item_name.lower())
        return item_config.get("building_type") if item_config else None
    
    def apply_npc_company_debuff(self, production: float, is_npc_owned: bool, building_type: str) -> float:
        """Stosuje debuff dla firm NPC"""
        if is_npc_owned and building_type == "Industrial Zone":
            return production / 3
        return production
    
    def apply_building_bonus(self, production: float, building_type: str, 
                           production_field_level: int, industrial_zone_level: int) -> float:
        """Stosuje bonus z poziomu budynku (5% per level)"""
        if building_type == "Production Field" and production_field_level > 0:
            production_field_level = max(0, min(5, production_field_level))
            return production * (1 + (production_field_level * 0.05))
        elif building_type == "Industrial Zone" and industrial_zone_level > 0:
            industrial_zone_level = max(0, min(5, industrial_zone_level))
            return production * (1 + (industrial_zone_level * 0.05))
        return production
    
    def apply_hospital_bonus(self, production: float, hospital_level: int) -> float:
        """Stosuje bonus ze szpitala (2% per level)"""
        if hospital_level > 0:
            hospital_level = max(0, min(5, hospital_level))
            return production * (1 + (hospital_level * 0.02))
        return production
    
    def apply_military_base_bonus(self, production: float, military_base_level: int, item_name: str) -> float:
        """Stosuje bonus z bazy wojskowej (5% dla broni i samolotów przy level 3+)"""
        if military_base_level >= 3 and item_name.lower() in ["weapon", "aircraft"]:
            return production * 1.05
        return production
    
    def apply_workers_debuff(self, production: float, workers_today: int) -> float:
        """Stosuje debuff od liczby pracowników"""
        worker_debuff = 1.3 - (workers_today / 10)
        return production * max(0.1, worker_debuff)  # Minimum 10% produkcji
    
    def apply_eco_skill_bonus(self, production: float, eco_skill: int) -> float:
        """Stosuje bonus od eco skill"""
        eco_bonus = 1 + (eco_skill / 50)
        return production * eco_bonus
    
    def apply_regional_and_country_bonus(self, production: float, regional_bonus: float, country_bonus: float) -> float:
        """Stosuje bonusy regionalne i krajowe"""
        total_bonus = regional_bonus + (country_bonus / 100.0)  # Konwersja procentów na ułamek
        return production + (production * total_bonus)
    
    def apply_pollution_debuff(self, production: float, pollution: float) -> float:
        """Stosuje debuff od zanieczyszczenia"""
        if pollution > 0:
            pollution_debuff = (production - (production * 0.1)) * (pollution / 100.0)
            return production - pollution_debuff
        return production
    
    def apply_company_sale_debuff(self, production: float, is_on_sale: bool) -> float:
        """Stosuje debuff dla firm na sprzedaż"""
        if is_on_sale:
            return production / 2
        return production
    
    def get_relevant_bonus(self, region_data: Dict[str, Any], item_name: str) -> Tuple[float, str]:
        """Pobiera odpowiedni bonus regionalny dla danego towaru"""
        bonus_description = region_data.get('bonus_description', '')
        
        if not bonus_description:
            return 0.0, "None"
        
        # Parse bonus description (format: "TICKETS:15" or "WEAPONS:20 TICKETS:15")
        bonus_by_type = self._parse_bonus_description(bonus_description)
        
        # Find relevant bonus for this item
        item_bonus_types = self.bonus_type_mapping.get(item_name.lower(), [])
        
        # ✅ DEBUG: Log oil/fuel bonus detection
        if item_name.lower() in ['fuel', 'oil']:
            region_name = region_data.get('region_name', region_data.get('name', 'Unknown'))
            print(f"🔍 DEBUG: Checking {item_name} bonus for region {region_name}")
            print(f"   Bonus description: '{bonus_description}'")
            print(f"   Parsed bonuses: {bonus_by_type}")
            print(f"   Looking for types: {item_bonus_types}")
        
        for bonus_type in item_bonus_types:
            if bonus_type.upper() in bonus_by_type:
                bonus_value = bonus_by_type[bonus_type.upper()] / 100.0
                # ✅ DEBUG: Log found bonus
                if item_name.lower() in ['fuel', 'oil']:
                    print(f"   ✅ Found {bonus_type.upper()} bonus: {bonus_value:.2%}")
                return bonus_value, bonus_type.upper()
        
        # ✅ DEBUG: Log no bonus found
        if item_name.lower() in ['fuel', 'oil']:
            print(f"   ❌ No bonus found for {item_name}")
        
        return 0.0, "None"
    
    def _parse_bonus_description(self, bonus_description: str) -> Dict[str, float]:
        """Parsuje opis bonusu w formacie 'TICKETS:15' lub 'WEAPONS:20 TICKETS:15'"""
        bonus_by_type = {}
        
        try:
            # Split by spaces to handle multiple bonuses
            parts = bonus_description.strip().split()
            
            for part in parts:
                if ':' in part:
                    bonus_type, bonus_value = part.split(':', 1)
                    try:
                        bonus_by_type[bonus_type.upper()] = float(bonus_value)
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error parsing bonus description '{bonus_description}': {e}")
        
        return bonus_by_type
    
    def calculate_country_bonus(self, country_name: str, item_name: str, all_regions: List[Dict[str, Any]] = None) -> float:
        """Oblicza bonus krajowy na podstawie wzoru: suma bonusów regionalnych danego typu w kraju / 5"""
        # Import region calculation service and delegate
        from src.core.services.calculations.region_calculation_service import RegionCalculationService
        
        if all_regions is None:
            # Try to load regions from database
            try:
                from src.data.database.models import load_regions_data
                all_regions, _ = load_regions_data()
            except Exception:
                return 0.0
        
        region_calc = RegionCalculationService()
        return region_calc.calculate_country_bonus(country_name, item_name, all_regions)
    
    def calculate_full_production(self, region_data: Dict[str, Any], item_name: str, 
                                factors: ProductionFactors) -> Optional[ProductionResult]:
        """
        Kompleksne obliczenie produkcji z wszystkimi czynnikami.
        
        Args:
            region_data: Dane regionu z API
            item_name: Nazwa towaru
            factors: Wszystkie czynniki wpływające na produkcję
            
        Returns:
            Wynik obliczeń produkcji lub None jeśli błąd
        """
        try:
            # Pobierz bazową produkcję dla towaru
            item_config = self.base_production.get(item_name.lower())
            if not item_config:
                return None
            
            building_type = item_config["building_type"]
            
            # Pobierz bazową produkcję dla danego tieru
            tier_key = f"q{factors.company_tier}"
            if tier_key not in item_config:
                tier_key = "q5"  # Fallback do Q5
            base_production = item_config[tier_key]
            
            # Pobierz dane regionu
            region_name = region_data.get("region_name", region_data.get("name", "Unknown"))
            country_id = region_data.get("country_id")
            country_name = region_data.get("country_name", "Unknown")
            pollution = region_data.get("pollution", 0)
            
            # Pobierz NPC wages dla kraju
            if not self.npc_wages_cache:
                self.load_npc_wages_data()
            npc_wages = self.npc_wages_cache.get(country_id, 5.0)
            
            # Walidacja poziomów budynków (0-5)
            factors.military_base_level = max(0, min(5, factors.military_base_level))
            factors.production_field_level = max(0, min(5, factors.production_field_level))
            factors.industrial_zone_level = max(0, min(5, factors.industrial_zone_level))
            factors.hospital_level = max(0, min(5, factors.hospital_level))
            
            # ===== OBLICZANIE PRODUKCJI ZGODNIE Z MECHANIKAMI ECLESIAR =====
            applied_factors = {}
            
            # 1. NPC Company Owner - produkcja dzielona przez 3 dla produktów
            production = float(base_production)
            production = self.apply_npc_company_debuff(production, factors.is_npc_owned, building_type)
            applied_factors["npc_debuff"] = production / base_production if base_production > 0 else 1.0
            
            # 2. Building bonuses (5% per level)
            old_production = production
            production = self.apply_building_bonus(
                production, building_type, 
                factors.production_field_level, factors.industrial_zone_level
            )
            applied_factors["building_bonus"] = production / old_production if old_production > 0 else 1.0
            
            # 3. Hospital bonus (2% per level)
            old_production = production
            production = self.apply_hospital_bonus(production, factors.hospital_level)
            applied_factors["hospital_bonus"] = production / old_production if old_production > 0 else 1.0
            
            # 4. Military base bonus (5% dla broni i air-weapons)
            old_production = production
            production = self.apply_military_base_bonus(production, factors.military_base_level, item_name)
            applied_factors["military_bonus"] = production / old_production if old_production > 0 else 1.0
            
            # 5. Consecutive workers debuff
            old_production = production
            production = self.apply_workers_debuff(production, factors.workers_today)
            applied_factors["workers_debuff"] = production / old_production if old_production > 0 else 1.0
            
            # 6. Eco skill bonus
            old_production = production
            production = self.apply_eco_skill_bonus(production, factors.eco_skill)
            applied_factors["eco_skill_bonus"] = production / old_production if old_production > 0 else 1.0
            
            # 7. Region and country bonus
            regional_bonus, bonus_type = self.get_relevant_bonus(region_data, item_name)
            country_bonus = self.calculate_country_bonus(country_name, item_name)
            old_production = production
            production = self.apply_regional_and_country_bonus(production, regional_bonus, country_bonus)
            applied_factors["regional_country_bonus"] = production / old_production if old_production > 0 else 1.0
            
            # 8. Pollution debuff
            old_production = production
            production = self.apply_pollution_debuff(production, pollution)
            applied_factors["pollution_debuff"] = production / old_production if old_production > 0 else 1.0
            
            # 9. Company state (on sale)
            old_production = production
            production = self.apply_company_sale_debuff(production, factors.is_on_sale)
            applied_factors["sale_debuff"] = production / old_production if old_production > 0 else 1.0
            
            # Zastosuj zaokrąglenie integer dla eco skill (zgodnie z dokumentacją)
            production = int(production)
            
            # Oblicz produkcję dla wszystkich jakości (używając proporcji)
            production_q1 = int(production * (item_config["q1"] / item_config[tier_key]))
            production_q2 = int(production * (item_config["q2"] / item_config[tier_key]))
            production_q3 = int(production * (item_config["q3"] / item_config[tier_key]))
            production_q4 = int(production * (item_config["q4"] / item_config[tier_key]))
            production_q5 = int(production * (item_config["q5"] / item_config[tier_key]))
            
            # Oblicz score efektywności (wyższy = lepszy)
            efficiency_score = (production_q5 * 5 + production_q4 * 4 + production_q3 * 3 + 
                              production_q2 * 2 + production_q1) / (5 + 4 + 3 + 2 + 1)
            
            return ProductionResult(
                region_name=region_name,
                country_name=country_name,
                country_id=country_id,
                item_name=item_name,
                total_bonus=regional_bonus + (country_bonus / 100.0),
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
                efficiency_score=efficiency_score,
                building_type=building_type,
                applied_factors=applied_factors
            )
            
        except Exception as e:
            print(f"Error calculating production for {region_data.get('name', 'Unknown')} - {item_name}: {e}")
            return None
    
    def get_available_items(self) -> List[str]:
        """Zwraca listę dostępnych towarów"""
        return list(self.base_production.keys())
    
    def get_item_info(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Zwraca informacje o towarze"""
        return self.base_production.get(item_name.lower())
