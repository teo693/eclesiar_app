#!/usr/bin/env python3
"""
Konfiguracja dla analizatora produkcji Eclesiar.
Pozwala na dostosowanie parametrów, które nie są dostępne w API.
"""

# ===== DOMYŚLNE WARTOŚCI DLA BRAKUJĄCYCH DANYCH =====

# Poziom firmy (1-5, gdzie 5 to najwyższa jakość)
DEFAULT_COMPANY_TIER = 5

# Eco skill gracza (0-100+)
# Domyślnie 16, bazowe wartości to produkcja z eco skill 0, bonus jest dodawany
DEFAULT_ECO_SKILL = 16

# Liczba pracowników, którzy pracowali dzisiaj w firmie
# Domyślnie 1, bo bazowe wartości to produkcja z 1 pracownikiem
DEFAULT_WORKERS_TODAY = 1

# Czy firma jest własnością NPC (True) czy gracza (False)
DEFAULT_IS_NPC_OWNED = False

# Poziom military base w regionie (0 = brak, 3+ = bonus 5% dla broni)
DEFAULT_MILITARY_BASE_LEVEL = 0

# Poziom Production Field w regionie (0 = brak, każdy poziom = +5% produkcji surowców)
DEFAULT_PRODUCTION_FIELD_LEVEL = 0

# Poziom Industrial Zone w regionie (0 = brak, każdy poziom = +5% produkcji produktów)
DEFAULT_INDUSTRIAL_ZONE_LEVEL = 0

# Czy firma jest na sprzedaż (True = produkcja / 2)
DEFAULT_IS_ON_SALE = False

# ===== KONFIGURACJA DLA RÓŻNYCH SCENARIUSZY =====

# Scenariusz: Gracz z wysokim eco skill (poziom 16)
HIGH_ECO_SKILL_CONFIG = {
    "default_company_tier": 5,
    "default_eco_skill": 16,  # Poziom 16 (wysoki eco skill)
    "default_workers_today": 1,  # 1 pracownik
    "default_is_npc_owned": False,
    "default_military_base_level": 0,  # TODO: Potrzebne dane z gry
    "default_production_field_level": 0,  # TODO: Potrzebne dane z gry
    "default_industrial_zone_level": 0,   # TODO: Potrzebne dane z gry
    "default_is_on_sale": False
}

# Scenariusz: Nowy gracz
NEW_PLAYER_CONFIG = {
    "default_company_tier": 1,  # Q1 firma
    "default_eco_skill": 0,     # Brak eco skill
    "default_workers_today": 1, # 1 pracownik (bazowe wartości)
    "default_is_npc_owned": False,
    "default_military_base_level": 0,  # Brak military base
    "default_production_field_level": 0,  # Brak production field
    "default_industrial_zone_level": 0,   # Brak industrial zone
    "default_is_on_sale": False
}

# Scenariusz: Firma NPC
NPC_COMPANY_CONFIG = {
    "default_company_tier": 5,
    "default_eco_skill": 0,     # NPC nie ma eco skill
    "default_workers_today": 5, # Więcej pracowników
    "default_is_npc_owned": True,  # Firma NPC
    "default_military_base_level": 0,
    "default_production_field_level": 1,
    "default_industrial_zone_level": 1,
    "default_is_on_sale": False
}

# Scenariusz: Firma na sprzedaż
COMPANY_ON_SALE_CONFIG = {
    "default_company_tier": 5,
    "default_eco_skill": 16,
    "default_workers_today": 0, # Brak pracowników
    "default_is_npc_owned": False,
    "default_military_base_level": 0,
    "default_production_field_level": 0,
    "default_industrial_zone_level": 0,
    "default_is_on_sale": True  # Firma na sprzedaż
}

# ===== FUNKCJE POMOCNICZE =====

def get_config(scenario: str = "default") -> dict:
    """
    Zwraca konfigurację dla danego scenariusza.
    
    Args:
        scenario: Nazwa scenariusza ("default", "high_eco", "new_player", "npc_company", "on_sale")
    
    Returns:
        Słownik z konfiguracją
    """
    configs = {
        "default": {
            "default_company_tier": DEFAULT_COMPANY_TIER,
            "default_eco_skill": DEFAULT_ECO_SKILL,
            "default_workers_today": DEFAULT_WORKERS_TODAY,
            "default_is_npc_owned": DEFAULT_IS_NPC_OWNED,
            "default_military_base_level": DEFAULT_MILITARY_BASE_LEVEL,
            "default_production_field_level": DEFAULT_PRODUCTION_FIELD_LEVEL,
            "default_industrial_zone_level": DEFAULT_INDUSTRIAL_ZONE_LEVEL,
            "default_is_on_sale": DEFAULT_IS_ON_SALE
        },
        "high_eco": HIGH_ECO_SKILL_CONFIG,
        "new_player": NEW_PLAYER_CONFIG,
        "npc_company": NPC_COMPANY_CONFIG,
        "on_sale": COMPANY_ON_SALE_CONFIG
    }
    
    return configs.get(scenario, configs["default"])

def print_available_scenarios():
    """Displays available configuration scenarios"""
    print("Available configuration scenarios:")
    print("1. default - Default values (Q5 company, eco skill 16, 1 worker)")
    print("2. high_eco - Player with high eco skill (16)")
    print("3. new_player - New player (Q1 company, eco skill 0)")
    print("4. npc_company - NPC company (production / 3 for products)")
    print("5. on_sale - Company for sale (production / 2)")

if __name__ == "__main__":
    print_available_scenarios()
    print("\nUsage example:")
    print("from production_config import get_config")
    print("config = get_config('high_eco')")
    print("analyzer.generate_production_report(regions_data, **config)")
