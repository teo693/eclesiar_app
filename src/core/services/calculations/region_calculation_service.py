"""
Region Calculation Service

Centralny serwis do obliczeń bonusów regionalnych i krajowych.
Implementuje logikę obliczania bonusów dla produkcji w różnych regionach.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class RegionRanking:
    """Ranking regionu dla konkretnego towaru"""
    region_name: str
    country_name: str
    country_id: int
    regional_bonus: float
    country_bonus: float
    total_bonus: float
    bonus_type: str
    pollution: float
    efficiency_score: float


@dataclass
class CountryBonusInfo:
    """Informacje o bonusie krajowym"""
    country_name: str
    bonus_type: str
    total_regional_bonus: float
    regions_count: int
    country_bonus: float


class RegionCalculationService:
    """Centralny serwis do obliczeń bonusów regionalnych i krajowych"""
    
    def __init__(self):
        # Mapowanie typów bonusów dla produktów
        self.bonus_type_mapping = {
            "aircraft": "AIRCRAFT",
            "air-weapon": "AIRCRAFT", 
            "samolot": "AIRCRAFT",
            "weapon": "WEAPONS",
            "broń": "WEAPONS",
            "iron": "IRON",
            "grain": "GRAIN",
            "zboże": "GRAIN",
            "food": "FOOD",
            "fuel": "OIL",
            "paliwo": "OIL",
            "titanium": "TITANIUM",
            "tytan": "TITANIUM",
            "airplane ticket": "TICKETS",
            "bilet lotniczy": "TICKETS"
        }
    
    def get_regional_bonus_for_item(self, region_data: Dict[str, Any], item_name: str) -> Tuple[float, str]:
        """
        Zwraca bonus regionalny i typ bonusu dla konkretnego towaru.
        
        Args:
            region_data: Dane regionu z API
            item_name: Nazwa towaru
            
        Returns:
            Tuple[bonus_value, bonus_type] - bonus w ułamku (np. 0.15 dla 15%) i typ bonusu
        """
        bonus_description = region_data.get('bonus_description', '')
        
        if not bonus_description:
            return 0.0, "None"
        
        # Parse bonus description (format: "TICKETS:15" or "WEAPONS:20 TICKETS:15")
        bonus_by_type = self._parse_bonus_description(bonus_description)
        
        # Określ typ bonusu dla danego towaru
        expected_bonus_type = self.bonus_type_mapping.get(item_name.lower(), "GRAIN")
        
        # Sprawdź czy region ma bonus dla tego typu
        if expected_bonus_type in bonus_by_type:
            bonus_value = bonus_by_type[expected_bonus_type]
            return bonus_value / 100.0, expected_bonus_type  # Konwersja na ułamek
        
        return 0.0, "None"
    
    def _parse_bonus_description(self, bonus_description: str) -> Dict[str, float]:
        """
        Parsuje opis bonusu w formacie "TICKETS:15" lub "WEAPONS:20 TICKETS:15"
        
        Args:
            bonus_description: Opis bonusu z API
            
        Returns:
            Dictionary mapping bonus types to values
        """
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
    
    def calculate_country_bonus(self, country_name: str, item_name: str, regions_data: List[Dict[str, Any]]) -> float:
        """
        Oblicza bonus krajowy na podstawie wzoru:
        suma bonusów regionalnych danego typu w kraju / 5 = bonus krajowy w %
        
        Args:
            country_name: Nazwa kraju
            item_name: Nazwa towaru
            regions_data: Lista regionów z bazy danych
            
        Returns:
            Bonus krajowy w procentach (jako float, np. 7.0 dla 7%)
        """
        try:
            # Znajdź wszystkie unikalne regiony w danym kraju (bez duplikatów)
            unique_regions = {}
            for region in regions_data:
                if region.get('country_name', '').lower() == country_name.lower():
                    region_key = region.get('region_name', region.get('name', '')).lower()
                    # Zachowaj tylko pierwszy (najnowszy) region o tej nazwie
                    if region_key not in unique_regions:
                        unique_regions[region_key] = region
            
            country_regions = list(unique_regions.values())
            
            if not country_regions:
                return 0.0
            
            # Określ typ bonusu dla danego towaru
            bonus_type = self.bonus_type_mapping.get(item_name.lower(), "GRAIN")
            
            # Zsumuj bonusy danego typu ze wszystkich unikalnych regionów w kraju
            total_bonus = 0.0
            regions_with_bonus = 0
            
            for region in country_regions:
                # Parsuj bonus_description do bonus_by_type
                bonus_description = region.get('bonus_description', '')
                if bonus_description:
                    bonus_by_type = self._parse_bonus_description(bonus_description)
                    if bonus_type in bonus_by_type:
                        bonus_value = bonus_by_type[bonus_type]
                        if bonus_value > 0:
                            total_bonus += bonus_value
                            regions_with_bonus += 1
            
            # Oblicz bonus krajowy: suma / 5
            if regions_with_bonus > 0:
                country_bonus = total_bonus / 5.0
                return country_bonus
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating country bonus for {country_name}: {e}")
            return 0.0
    
    def get_country_bonus_info(self, country_name: str, item_name: str, regions_data: List[Dict[str, Any]]) -> CountryBonusInfo:
        """
        Zwraca szczegółowe informacje o bonusie krajowym.
        
        Args:
            country_name: Nazwa kraju
            item_name: Nazwa towaru
            regions_data: Lista regionów
            
        Returns:
            Szczegółowe informacje o bonusie krajowym
        """
        bonus_type = self.bonus_type_mapping.get(item_name.lower(), "GRAIN")
        
        # Znajdź wszystkie unikalne regiony w danym kraju
        unique_regions = {}
        for region in regions_data:
            if region.get('country_name', '').lower() == country_name.lower():
                region_key = region.get('region_name', region.get('name', '')).lower()
                if region_key not in unique_regions:
                    unique_regions[region_key] = region
        
        country_regions = list(unique_regions.values())
        
        # Oblicz sumę bonusów
        total_bonus = 0.0
        regions_with_bonus = 0
        
        for region in country_regions:
            bonus_description = region.get('bonus_description', '')
            if bonus_description:
                bonus_by_type = self._parse_bonus_description(bonus_description)
                if bonus_type in bonus_by_type:
                    bonus_value = bonus_by_type[bonus_type]
                    if bonus_value > 0:
                        total_bonus += bonus_value
                        regions_with_bonus += 1
        
        country_bonus = total_bonus / 5.0 if regions_with_bonus > 0 else 0.0
        
        return CountryBonusInfo(
            country_name=country_name,
            bonus_type=bonus_type,
            total_regional_bonus=total_bonus,
            regions_count=regions_with_bonus,
            country_bonus=country_bonus
        )
    
    def find_best_regions_for_item(self, item_name: str, regions_data: List[Dict[str, Any]], 
                                 top_n: int = 10) -> List[RegionRanking]:
        """
        Znajduje najlepsze regiony do produkcji konkretnego towaru.
        
        Args:
            item_name: Nazwa towaru
            regions_data: Lista wszystkich regionów
            top_n: Liczba najlepszych regionów do zwrócenia
            
        Returns:
            Lista najlepszych regionów posortowana według efektywności
        """
        rankings = []
        
        # Grupuj regiony według krajów dla obliczenia bonusów krajowych
        regions_by_country = {}
        for region in regions_data:
            country_name = region.get('country_name', 'Unknown')
            if country_name not in regions_by_country:
                regions_by_country[country_name] = []
            regions_by_country[country_name].append(region)
        
        for region in regions_data:
            try:
                region_name = region.get('region_name', region.get('name', 'Unknown'))
                country_name = region.get('country_name', 'Unknown')
                country_id = region.get('country_id', 0)
                pollution = region.get('pollution', 0)
                
                # Oblicz bonus regionalny
                regional_bonus, bonus_type = self.get_regional_bonus_for_item(region, item_name)
                
                # Oblicz bonus krajowy
                country_bonus = self.calculate_country_bonus(country_name, item_name, regions_data)
                
                # Oblicz całkowity bonus
                total_bonus = regional_bonus + (country_bonus / 100.0)
                
                # Oblicz score efektywności (uwzględnia bonus i pollution)
                efficiency_score = self.calculate_region_efficiency_score(region, item_name, total_bonus)
                
                ranking = RegionRanking(
                    region_name=region_name,
                    country_name=country_name,
                    country_id=country_id,
                    regional_bonus=regional_bonus,
                    country_bonus=country_bonus,
                    total_bonus=total_bonus,
                    bonus_type=bonus_type,
                    pollution=pollution,
                    efficiency_score=efficiency_score
                )
                rankings.append(ranking)
                
            except Exception as e:
                print(f"Error processing region {region.get('name', 'Unknown')}: {e}")
                continue
        
        # Sortuj według efficiency_score i zwróć top N
        rankings.sort(key=lambda x: x.efficiency_score, reverse=True)
        return rankings[:top_n]
    
    def calculate_region_efficiency_score(self, region_data: Dict[str, Any], item_name: str, 
                                        total_bonus: float = None) -> float:
        """
        Oblicza ogólny wskaźnik efektywności regionu dla danego towaru.
        
        Args:
            region_data: Dane regionu
            item_name: Nazwa towaru
            total_bonus: Preobliczony całkowity bonus (opcjonalne)
            
        Returns:
            Wskaźnik efektywności (wyższy = lepszy)
        """
        try:
            # Jeśli nie podano total_bonus, oblicz go
            if total_bonus is None:
                regional_bonus, _ = self.get_regional_bonus_for_item(region_data, item_name)
                country_name = region_data.get('country_name', 'Unknown')
                country_bonus = self.calculate_country_bonus(country_name, item_name, [region_data])
                total_bonus = regional_bonus + (country_bonus / 100.0)
            
            # Pobierz pollution
            pollution = region_data.get('pollution', 0)
            
            # Oblicz score bazowy z bonusów (konwersja na procenty)
            bonus_score = total_bonus * 100
            
            # Odejmij pollution penalty (pollution obniża efektywność)
            pollution_penalty = pollution * 0.5  # Pollution ma mniejszy wpływ niż bonusy
            
            # Wynik: bonus - pollution penalty, minimum 0
            efficiency_score = max(0, bonus_score - pollution_penalty)
            
            return efficiency_score
            
        except Exception as e:
            print(f"Error calculating efficiency score: {e}")
            return 0.0
    
    def get_regions_by_country(self, regions_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Grupuje regiony według krajów.
        
        Args:
            regions_data: Lista regionów
            
        Returns:
            Słownik mapujący nazwy krajów na listy regionów
        """
        regions_by_country = {}
        
        for region in regions_data:
            country_name = region.get('country_name', 'Unknown')
            if country_name not in regions_by_country:
                regions_by_country[country_name] = []
            regions_by_country[country_name].append(region)
        
        return regions_by_country
    
    def get_bonus_types_in_region(self, region_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Zwraca wszystkie typy bonusów dostępne w regionie.
        
        Args:
            region_data: Dane regionu
            
        Returns:
            Słownik mapujący typy bonusów na wartości
        """
        bonus_description = region_data.get('bonus_description', '')
        if not bonus_description:
            return {}
        
        return self._parse_bonus_description(bonus_description)
    
    def get_countries_ranking_for_item(self, item_name: str, regions_data: List[Dict[str, Any]]) -> List[CountryBonusInfo]:
        """
        Zwraca ranking krajów dla danego towaru.
        
        Args:
            item_name: Nazwa towaru
            regions_data: Lista regionów
            
        Returns:
            Lista krajów posortowana według bonusu krajowego
        """
        countries = set(region.get('country_name', 'Unknown') for region in regions_data)
        country_rankings = []
        
        for country_name in countries:
            if country_name != 'Unknown':
                country_info = self.get_country_bonus_info(country_name, item_name, regions_data)
                country_rankings.append(country_info)
        
        # Sortuj według bonusu krajowego
        country_rankings.sort(key=lambda x: x.country_bonus, reverse=True)
        return country_rankings
