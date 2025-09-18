"""
Database-First Orchestrator Service

Nowy orchestrator implementujący przepływ zgodny z planem refaktoryzacji:
1. Aktualizacja bazy danych
2. Generowanie raportów z bazy danych (bez cache)

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.core.services.database_manager_service import DatabaseManagerService
from src.core.services.calculations.currency_calculation_service import CurrencyCalculationService
from src.core.services.calculations.production_calculation_service import ProductionCalculationService
from src.core.services.calculations.region_calculation_service import RegionCalculationService
from src.core.services.calculations.market_calculation_service import MarketCalculationService
from src.reports.generators.daily_report import generate_report
from src.reports.generators.html_report import generate_html_report
from src.reports.generators.production_report import ProductionAnalyzer
from src.reports.generators.arbitrage_report import CurrencyArbitrageAnalyzer
from src.reports.generators.short_economic_report import generate_short_economic_report
from src.data.storage.cache import save_historical_data, load_historical_data


class DatabaseFirstOrchestrator:
    """
    Orchestrator implementujący przepływ DB-first zgodnie z planem refaktoryzacji.
    
    Przepływ:
    1. Sprawdza czy baza danych jest świeża
    2. Jeśli nie - aktualizuje bazę danych z API
    3. Generuje raporty wyłącznie z danych z bazy danych
    4. Używa centralnych serwisów obliczeniowych
    """
    
    def __init__(self, db_path: str = None, force_refresh: bool = False):
        self.db_manager = DatabaseManagerService(db_path)
        self.force_refresh = force_refresh
        
        # Inicjalizuj centralne serwisy obliczeniowe
        self.currency_calc = CurrencyCalculationService(cache_timeout_minutes=0)  # Bez cache
        self.production_calc = ProductionCalculationService(db_path)
        self.region_calc = RegionCalculationService()
        self.market_calc = MarketCalculationService()
        
        print("🏗️ Database-First Orchestrator initialized")
        print("📊 Using centralized calculation services")
        print("🚫 Cache disabled - all data from database")
    
    def run(self, sections: Dict[str, bool] = None, report_type: str = "daily", 
            output_dir: str = "reports") -> str:
        """
        Główna metoda orchestratora - przepływ DB-first.
        
        Args:
            sections: Sekcje do włączenia w raport
            report_type: Typ raportu do wygenerowania
            output_dir: Katalog wyjściowy
            
        Returns:
            Ścieżka do wygenerowanego raportu lub komunikat o błędzie
        """
        if sections is None:
            sections = {
                'military': True,
                'warriors': True, 
                'economic': True,
                'production': True
            }
        
        print(f"🚀 Starting Database-First Orchestrator...")
        print(f"📊 Report type: {report_type}")
        print(f"📁 Output directory: {output_dir}")
        
        try:
            # KROK 1: Sprawdź świeżość bazy danych i zaktualizuj jeśli potrzeba
            if not self._ensure_fresh_database(sections):
                return "❌ Failed to update database"
            
            # KROK 2: Pobierz wszystkie dane z bazy danych
            data_bundle = self._load_data_from_database(sections)
            if not data_bundle:
                return "❌ Failed to load data from database"
            
            # KROK 3: Wygeneruj raport używając centralnych serwisów
            report_path = self._generate_report_from_db_data(
                data_bundle, sections, report_type, output_dir
            )
            
            if report_path:
                print(f"✅ Report generated successfully: {report_path}")
                return report_path
            else:
                return "❌ Failed to generate report"
                
        except Exception as e:
            print(f"❌ Error in Database-First Orchestrator: {e}")
            return f"❌ Error: {e}"
    
    def _ensure_fresh_database(self, sections: Dict[str, bool]) -> bool:
        """
        Zapewnia że baza danych jest świeża.
        Aktualizuje bazę danych jeśli jest przestarzała lub wymuszono odświeżenie.
        """
        # Sprawdź czy baza jest świeża (max 1 godzina)
        if not self.force_refresh and self.db_manager.is_database_fresh(max_age_hours=1):
            last_refresh = self.db_manager.get_last_refresh_time()
            print(f"✅ Database is fresh (last updated: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')})")
            return True
        
        # Baza danych wymaga aktualizacji
        print("🔄 Database needs refresh, updating from API...")
        return self.db_manager.update_database_full(sections)
    
    def _load_data_from_database(self, sections: Dict[str, bool]) -> Optional[Dict[str, Any]]:
        """
        Ładuje wszystkie potrzebne dane z bazy danych.
        
        Returns:
            Słownik z danymi lub None jeśli nie udało się załadować
        """
        print("📚 Loading data from database...")
        
        try:
            data_bundle = {}
            
            # Podstawowe dane ekonomiczne (zawsze potrzebne)
            data_bundle['countries'] = self.db_manager.get_countries_data()
            data_bundle['currencies_map'] = self.db_manager.get_currencies_data()
            data_bundle['currency_rates'] = self.db_manager.get_currency_rates()
            
            # Znajdź GOLD ID
            gold_id = None
            for curr_id, curr_name in data_bundle['currencies_map'].items():
                if curr_name.upper() == 'GOLD':
                    gold_id = curr_id
                    break
            data_bundle['gold_id'] = gold_id or 1  # Fallback
            
            # Dane ekonomiczne
            if sections.get('economic', False):
                data_bundle['job_offers'] = self.db_manager.get_job_offers()
                data_bundle['market_offers'] = self.db_manager.get_market_offers()
                
                # Przetwórz oferty na format oczekiwany przez raporty
                data_bundle['best_jobs'] = self._process_job_offers(data_bundle['job_offers'])
                data_bundle['cheapest_items'] = self._process_market_offers(data_bundle['market_offers'])
            
            # Dane regionów (dla produktywności)
            if sections.get('production', False):
                regions_data, regions_summary = self.db_manager.get_regions_data()
                data_bundle['regions_data'] = regions_data
                data_bundle['regions_summary'] = regions_summary
            
            # Dane militarne
            if sections.get('military', False):
                hits_data, wars_summary = self.db_manager.get_military_data()
                data_bundle['hits_data'] = hits_data
                data_bundle['wars_summary'] = wars_summary
            
            # Dane wojowników
            if sections.get('warriors', False):
                data_bundle['warriors_data'] = self.db_manager.get_warriors_data()
            
            # Czas pobrania danych
            data_bundle['fetched_at'] = datetime.now().isoformat()
            
            print("✅ All data loaded from database successfully")
            return data_bundle
            
        except Exception as e:
            print(f"❌ Error loading data from database: {e}")
            return None
    
    def _process_job_offers(self, job_offers: List[Dict]) -> List[Dict]:
        """Przetwarza oferty pracy do formatu oczekiwanego przez raporty"""
        processed = []
        for job in job_offers[:50]:  # Top 50 ofert
            processed.append({
                'country_id': job.get('country_id'),
                'country_name': job.get('country_name'),
                'wage': job.get('wage_original'),
                'wage_gold': job.get('wage_gold'),
                'currency_id': job.get('currency_id'),
                'currency_name': job.get('currency_name'),
                'job_title': job.get('job_title', 'Unknown'),
                'business_name': job.get('business_name', 'Unknown'),
                'business_id': job.get('country_id', 0)  # Fallback dla kompatybilności
            })
        return processed
    
    def _process_market_offers(self, market_offers: List[Dict]) -> List[Dict]:
        """Przetwarza oferty rynkowe do formatu oczekiwanego przez raporty"""
        processed = []
        for offer in market_offers[:100]:  # Top 100 najtańszych
            processed.append({
                'item_id': offer.get('item_id'),
                'item_name': offer.get('item_name'),
                'country_id': offer.get('country_id'),
                'country_name': offer.get('country_name'),
                'price': offer.get('price_original'),
                'price_gold': offer.get('price_gold'),
                'currency_id': offer.get('currency_id'),
                'currency_name': offer.get('currency_name'),
                'quantity': offer.get('quantity', 1)
            })
        return processed
    
    def _generate_report_from_db_data(self, data_bundle: Dict[str, Any], 
                                    sections: Dict[str, bool], report_type: str, 
                                    output_dir: str) -> Optional[str]:
        """
        Generuje raport używając danych z bazy danych i centralnych serwisów obliczeniowych.
        """
        print(f"📋 Generating {report_type} report from database data...")
        
        try:
            if report_type == "daily":
                return self._generate_daily_report(data_bundle, sections, output_dir)
            
            elif report_type == "html":
                return self._generate_html_report(data_bundle, sections, output_dir)
            
            elif report_type == "production":
                return self._generate_production_report(data_bundle, output_dir)
            
            elif report_type == "arbitrage":
                return self._generate_arbitrage_report(data_bundle, output_dir)
            
            elif report_type == "short_economic":
                return self._generate_short_economic_report(data_bundle, output_dir)
            
            elif report_type == "google_sheets":
                return self._generate_google_sheets_report(data_bundle, sections, output_dir)
            
            else:
                print(f"❌ Unknown report type: {report_type}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating {report_type} report: {e}")
            return None
    
    def _generate_daily_report(self, data_bundle: Dict[str, Any], 
                             sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generuje dzienny raport DOCX z danych z bazy"""
        
        # Przygotuj dane w formacie oczekiwanym przez generator
        summary_data = {
            'fetched_at': data_bundle.get('fetched_at'),
            'total_countries': len(data_bundle.get('countries', [])),
            'total_currencies': len(data_bundle.get('currencies_map', {}))
        }
        
        # Załaduj dane historyczne dla porównań
        historical_data = load_historical_data()
        
        # Przygotuj top wojowników
        warriors_data = data_bundle.get('warriors_data', [])
        top_warriors = warriors_data[:10] if warriors_data else []
        
        # Generuj raport używając istniejącego generatora
        return generate_report(
            summary_data=summary_data,
            historical_data=historical_data,
            top_warriors=top_warriors,
            items_map={},  # TODO: Dodać items_map do bazy danych
            currencies_map=data_bundle.get('currencies_map', {}),
            country_map={c['country_id']: c['country_name'] for c in data_bundle.get('countries', [])},
            currency_codes_map={},  # TODO: Dodać currency_codes_map
            gold_id=data_bundle.get('gold_id'),
            output_dir=output_dir,
            sections=sections
        )
    
    def _generate_html_report(self, data_bundle: Dict[str, Any], 
                            sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generuje dzienny raport HTML z danych z bazy"""
        
        # Analogicznie do daily report, ale z HTML generator
        summary_data = {
            'fetched_at': data_bundle.get('fetched_at'),
            'total_countries': len(data_bundle.get('countries', [])),
            'total_currencies': len(data_bundle.get('currencies_map', {}))
        }
        
        historical_data = load_historical_data()
        warriors_data = data_bundle.get('warriors_data', [])
        top_warriors = warriors_data[:10] if warriors_data else []
        
        return generate_html_report(
            summary_data=summary_data,
            historical_data=historical_data,
            top_warriors=top_warriors,
            items_map={},
            currencies_map=data_bundle.get('currencies_map', {}),
            country_map={c['country_id']: c['country_name'] for c in data_bundle.get('countries', [])},
            currency_codes_map={},
            gold_id=data_bundle.get('gold_id'),
            output_dir=output_dir,
            sections=sections
        )
    
    def _generate_production_report(self, data_bundle: Dict[str, Any], 
                                  output_dir: str) -> Optional[str]:
        """Generuje raport produktywności używając centralnych serwisów"""
        
        regions_data = data_bundle.get('regions_data', [])
        if not regions_data:
            print("❌ No regions data available for production report")
            return None
        
        # Użyj refaktoryzowanego ProductionAnalyzer
        analyzer = ProductionAnalyzer()
        
        # Generuj raport - analyzer już używa centralnych serwisów
        report_path = analyzer.generate_production_report(
            regions_data=regions_data,
            output_format="txt",
            default_company_tier=5,
            default_eco_skill=0
        )
        
        return report_path
    
    def _generate_arbitrage_report(self, data_bundle: Dict[str, Any], 
                                 output_dir: str) -> Optional[str]:
        """Generuje raport arbitrażu walutowego używając centralnych serwisów"""
        
        currency_rates = data_bundle.get('currency_rates', {})
        currencies_map = data_bundle.get('currencies_map', {})
        
        if not currency_rates:
            print("❌ No currency rates available for arbitrage report")
            return None
        
        # Użyj refaktoryzowanego CurrencyArbitrageAnalyzer
        analyzer = CurrencyArbitrageAnalyzer(min_profit_threshold=0.5)
        
        # Znajdź okazje arbitrażowe
        opportunities = analyzer.find_arbitrage_opportunities()
        
        if opportunities:
            return analyzer.generate_arbitrage_report(opportunities, "txt")
        else:
            print("❌ No arbitrage opportunities found")
            return None
    
    def _generate_short_economic_report(self, data_bundle: Dict[str, Any], 
                                      output_dir: str) -> Optional[str]:
        """Generuje krótki raport ekonomiczny"""
        
        # TODO: Przystosuj generator do pracy z danymi z bazy
        # Na razie użyj istniejącej funkcji która sama pobiera dane
        return generate_short_economic_report(output_dir)
    
    def _generate_google_sheets_report(self, data_bundle: Dict[str, Any], 
                                     sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generuje raport Google Sheets"""
        
        # TODO: Implementuj generator Google Sheets używający danych z bazy
        print("📊 Google Sheets report generation from database not yet implemented")
        return None
    
    def update_database_force(self, sections: Dict[str, bool] = None) -> bool:
        """Wymusza aktualizację bazy danych"""
        print("🔄 Forcing database update...")
        return self.db_manager.update_database_full(sections)
    
    def get_database_info(self) -> Dict[str, Any]:
        """Zwraca informacje o stanie bazy danych"""
        last_refresh = self.db_manager.get_last_refresh_time()
        is_fresh = self.db_manager.is_database_fresh()
        
        return {
            'last_refresh': last_refresh.strftime('%Y-%m-%d %H:%M:%S') if last_refresh else 'Never',
            'is_fresh': is_fresh,
            'max_age_hours': 1,
            'db_path': self.db_manager.db_path
        }
