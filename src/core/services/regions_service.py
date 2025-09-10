from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from src.data.api.client import fetch_data
from config.settings.base import GOLD_ID_FALLBACK


def fetch_regions_for_country(country_id: int) -> List[Dict[str, Any]]:
    """
    Pobiera regiony dla konkretnego kraju.
    
    Args:
        country_id: ID kraju
        
    Returns:
        Lista regionów z danego kraju
    """
    try:
        url = f"country/regions?country_id={country_id}"
        response = fetch_data(url, f"regionach kraju {country_id}")
        
        if response and response.get("code") == 200:
            return response.get("data", [])
        return []
    except Exception as e:
        print(f"Error fetching regions for country {country_id}: {e}")
        return []


def fetch_all_regions_with_bonuses(eco_countries: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Pobiera wszystkie regiony ze wszystkich krajów i filtruje tylko te z bonusami.
    
    Args:
        eco_countries: Słownik z informacjami o krajach
        
    Returns:
        Lista regionów z bonusami
    """
    regions_with_bonuses = []
    max_workers = int(os.getenv("API_WORKERS_REGIONS", "8"))
    
    def fetch_country_regions(country_id: int) -> List[Dict[str, Any]]:
        regions = fetch_regions_for_country(country_id)
        # Filtruj tylko regiony z bonusami
        regions_with_bonus = []
        for region in regions:
            if region.get("bonus") and len(region["bonus"]) > 0:
                regions_with_bonus.append(region)
        return regions_with_bonus
    
    # Parallel fetching of regions for all countries
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_country_regions, cid): cid for cid in eco_countries.keys()}
        
        for future in as_completed(futures):
            try:
                country_regions = future.result()
                regions_with_bonuses.extend(country_regions)
            except Exception as e:
                country_id = futures[future]
                print(f"Error fetching regions for country {country_id}: {e}")
    
    return regions_with_bonuses


def process_regions_data(regions: List[Dict[str, Any]], eco_countries: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Przetwarza dane regionów i przygotowuje je do wyświetlenia w tabeli.
    
    Args:
        regions: Lista regionów z bonusami
        eco_countries: Słownik z informacjami o krajach
        
    Returns:
        Lista przetworzonych regionów gotowa do wyświetlenia
    """
    processed_regions = []
    
    for region in regions:
        country_id = region.get("country_id")
        original_country_id = region.get("original_country_id")
        
        # Pobierz nazwę kraju
        country_name = "Unknown"
        if country_id in eco_countries:
            country_name = eco_countries[country_id].get("name", "Unknown")
        
        # Oblicz bonus_score (suma wszystkich bonusów) i przechowuj bonusy według typów
        bonus_score = 0
        bonus_description = ""
        bonus_by_type = {}  # Nowe: przechowuj bonusy według typów
        if region.get("bonus"):
            bonus_parts = []
            for bonus in region["bonus"]:
                bonus_type = bonus.get("type", "")
                bonus_value = bonus.get("value", 0)
                bonus_score += bonus_value
                bonus_parts.append(f"{bonus_type}:{bonus_value}")
                bonus_by_type[bonus_type] = bonus_value  # Przechowuj bonus według typu
            bonus_description = " ".join(bonus_parts)
        
        # Oblicz bonus_per_pollution
        pollution = region.get("pollution", 0)
        bonus_per_pollution = round(bonus_score / pollution, 2) if pollution > 0 else 0
        
        processed_region = {
            "region_name": region.get("name", "Unknown"),
            "country_name": country_name,
            "country_id": country_id,
            "pollution": pollution,
            "bonus_score": bonus_score,
            "bonus_description": bonus_description,
            "bonus_by_type": bonus_by_type,  # Nowe: bonusy według typów
            "population": region.get("population", 0),
            "nb_npcs": region.get("nb_npcs", 0),
            "type": region.get("type", 0),
            "original_country_id": original_country_id,
            "bonus_per_pollution": bonus_per_pollution
        }
        
        processed_regions.append(processed_region)
    
    # Sortuj według pollution od najniższego do najwyższego
    processed_regions.sort(key=lambda x: x["pollution"])
    
    return processed_regions


def get_regions_summary(regions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tworzy podsumowanie danych o regionach.
    
    Args:
        regions_data: Lista przetworzonych regionów
        
    Returns:
        Słownik z podsumowaniem
    """
    if not regions_data:
        return {}
    
    total_regions = len(regions_data)
    total_bonus_score = sum(r["bonus_score"] for r in regions_data)
    avg_pollution = sum(r["pollution"] for r in regions_data) / total_regions
    avg_bonus_per_pollution = sum(r["bonus_per_pollution"] for r in regions_data) / total_regions
    
    # Znajdź regiony z najwyższym i najniższym bonus_per_pollution
    best_efficiency = max(regions_data, key=lambda x: x["bonus_per_pollution"])
    worst_efficiency = min(regions_data, key=lambda x: x["bonus_per_pollution"])
    
    return {
        "total_regions": total_regions,
        "total_bonus_score": total_bonus_score,
        "average_pollution": round(avg_pollution, 2),
        "average_bonus_per_pollution": round(avg_bonus_per_pollution, 2),
        "best_efficiency_region": best_efficiency["region_name"],
        "best_efficiency_score": best_efficiency["bonus_per_pollution"],
        "worst_efficiency_region": worst_efficiency["region_name"],
        "worst_efficiency_score": worst_efficiency["bonus_per_pollution"]
    }


def fetch_and_process_regions(eco_countries: Dict[int, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Główna funkcja do pobierania i przetwarzania danych o regionach.
    
    Args:
        eco_countries: Słownik z informacjami o krajach
        
    Returns:
        Krotka (lista regionów, podsumowanie)
    """
    print("Fetching region data with bonuses...")
    
    # Pobierz wszystkie regiony z bonusami
    regions = fetch_all_regions_with_bonuses(eco_countries)
    
    if not regions:
        print("No regions with bonuses found.")
        return [], {}
    
    print(f"Found {len(regions)} regions with bonuses.")
    
    # Przetwórz dane
    processed_regions = process_regions_data(regions, eco_countries)
    
    # Utwórz podsumowanie
    summary = get_regions_summary(processed_regions)
    
    return processed_regions, summary


def compare_regions_with_history(current_regions: List[Dict[str, Any]], historical_regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Porównuje aktualne dane regionów z historycznymi i dodaje wskaźniki zmian.
    
    Args:
        current_regions: Aktualne dane regionów
        historical_regions: Historyczne dane regionów
        
    Returns:
        Lista regionów z wskaźnikami zmian
    """
    if not historical_regions:
        return current_regions
    
    # Utwórz mapę historycznych danych według region_name + country_id
    historical_map = {}
    for region in historical_regions:
        key = f"{region['region_name']}_{region['country_id']}"
        historical_map[key] = region
    
    # Dodaj wskaźniki zmian
    for region in current_regions:
        key = f"{region['region_name']}_{region['country_id']}"
        historical_region = historical_map.get(key)
        
        if historical_region:
            # Porównaj pollution
            old_pollution = historical_region.get("pollution", 0)
            new_pollution = region.get("pollution", 0)
            
            if new_pollution > old_pollution:
                region["pollution_change"] = "↑"
            elif new_pollution < old_pollution:
                region["pollution_change"] = "↓"
            else:
                region["pollution_change"] = "→"
            
            # Porównaj bonus_score
            old_bonus = historical_region.get("bonus_score", 0)
            new_bonus = region.get("bonus_score", 0)
            
            if new_bonus > old_bonus:
                region["bonus_change"] = "↑"
            elif new_bonus < old_bonus:
                region["bonus_change"] = "↓"
            else:
                region["bonus_change"] = "→"
            
            # Porównaj population
            old_population = historical_region.get("population", 0)
            new_population = region.get("population", 0)
            
            if new_population > old_population:
                region["population_change"] = "↑"
            elif new_population < old_population:
                region["population_change"] = "↓"
            else:
                region["population_change"] = "→"
        else:
            # Nowy region
            region["pollution_change"] = "🆕"
            region["bonus_change"] = "🆕"
            region["population_change"] = "🆕"
    
    return current_regions
