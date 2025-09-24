"""
Database-First Orchestrator Service

New orchestrator implementing DB-first flow according to refactoring plan:
1. Database update
2. Report generation from database (without cache)

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
    Orchestrator implementing DB-first flow according to refactoring plan.
    
    Flow:
    1. Checks if database is fresh
    2. If not - updates database from API
    3. Generates reports exclusively from database data
    4. Uses centralized calculation services
    """
    
    def __init__(self, db_path: str = None, force_refresh: bool = False):
        self.db_manager = DatabaseManagerService(db_path)
        self.force_refresh = force_refresh
        
        # Initialize centralized calculation services
        self.currency_calc = CurrencyCalculationService(cache_timeout_minutes=0)  # No cache
        self.production_calc = ProductionCalculationService(db_path)
        self.region_calc = RegionCalculationService()
        self.market_calc = MarketCalculationService()
        
        # Initialize service dependencies for report generators
        self._init_service_dependencies()
        
        print("🏗️ Database-First Orchestrator initialized")
        print("📊 Using centralized calculation services")
        print("🚫 Cache disabled - all data from database")
    
    def _init_service_dependencies(self):
        """Initialize service dependencies for report generators"""
        from ...core.services.base_service import ServiceDependencies
        from ...data.repositories.sqlite_repository import (
            SQLiteCountryRepository, SQLiteCurrencyRepository, SQLiteRegionRepository
        )
        
        # Create repository instances
        country_repo = SQLiteCountryRepository(self.db_manager.db_path)
        currency_repo = SQLiteCurrencyRepository(self.db_manager.db_path)
        region_repo = SQLiteRegionRepository(self.db_manager.db_path)
        
        # Create service dependencies
        self.deps = ServiceDependencies(
            country_repo=country_repo,
            currency_repo=currency_repo,
            region_repo=region_repo,
            item_repo=None,      # Will be implemented later
            market_repo=None,    # Will be implemented later
            production_repo=None, # Will be implemented later
            report_repo=None     # Will be implemented later
        )
    
    def run(self, sections: Dict[str, bool] = None, report_type: str = "daily", 
            output_dir: str = "reports") -> str:
        """
        Main orchestrator method - DB-first flow.
        
        Args:
            sections: Sections to include in report
            report_type: Type of report to generate
            output_dir: Output directory
            
        Returns:
            Path to generated report or error message
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
            # STEP 1: Check database freshness and update if needed
            if not self._ensure_fresh_database(sections):
                return "❌ Failed to update database"
            
            # STEP 2: Load all data from database
            data_bundle = self._load_data_from_database(sections)
            if not data_bundle:
                return "❌ Failed to load data from database"
            
            # STEP 3: Generate report using centralized services
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
        Ensures that the database is fresh.
        Updates database if it's outdated or refresh is forced.
        """
        # Check if database is fresh (max 1 minute)
        if not self.force_refresh and self.db_manager.is_database_fresh(max_age_hours=0.017):
            last_refresh = self.db_manager.get_last_refresh_time()
            print(f"✅ Database is fresh (last updated: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')})")
            return True
        
        # Database requires update
        print("🔄 Database needs refresh, updating from API...")
        return self.db_manager.update_database_full(sections)
    
    def _load_data_from_database(self, sections: Dict[str, bool]) -> Optional[Dict[str, Any]]:
        """
        Loads all necessary data from the database.
        
        Returns:
            Dictionary with data or None if loading failed
        """
        print("📚 Loading data from database...")
        
        try:
            data_bundle = {}
            
            # Basic economic data (always needed)
            data_bundle['countries'] = self.db_manager.get_countries_data()
            data_bundle['currencies_map'] = self.db_manager.get_currencies_data()
            data_bundle['currency_codes_map'] = self.db_manager.get_currency_codes_data()
            data_bundle['currency_rates'] = self.db_manager.get_currency_rates()
            data_bundle['items_map'] = self.db_manager.get_items_map()
            
            # Find GOLD ID
            gold_id = None
            for curr_id, curr_name in data_bundle['currencies_map'].items():
                if curr_name.upper() == 'GOLD':
                    gold_id = curr_id
                    break
            data_bundle['gold_id'] = gold_id or 1  # Fallback
            
            # Economic data (always load basic economic data if available)
            data_bundle['job_offers'] = self.db_manager.get_job_offers()
            data_bundle['market_offers'] = self.db_manager.get_market_offers()
            
            # Process offers to format expected by reports
            data_bundle['best_jobs'] = self._process_job_offers(data_bundle['job_offers']) if data_bundle['job_offers'] else []
            data_bundle['cheapest_items'] = self._process_market_offers(data_bundle['market_offers']) if data_bundle['market_offers'] else {}
            
            # Region data (always load for comprehensive economic analysis)
            regions_data, regions_summary = self.db_manager.get_regions_data()
            # Fix country names in regions_data if they are 'Unknown'
            regions_data = self._fix_regions_country_names(regions_data, data_bundle['countries'])
            data_bundle['regions_data'] = regions_data
            data_bundle['regions_summary'] = regions_summary
            
            # Military data
            if sections.get('military', False):
                hits_data, wars_summary = self.db_manager.get_military_data()
                data_bundle['hits_data'] = hits_data
                data_bundle['wars_summary'] = wars_summary
            
            # Warriors data
            if sections.get('warriors', False):
                data_bundle['warriors_data'] = self.db_manager.get_warriors_data()
            
            # Data fetch time
            data_bundle['fetched_at'] = datetime.now().isoformat()
            
            print("✅ All data loaded from database successfully")
            return data_bundle
            
        except Exception as e:
            print(f"❌ Error loading data from database: {e}")
            return None
    
    def _process_job_offers(self, job_offers: List[Dict]) -> List[Dict]:
        """Processes job offers to format expected by reports"""
        processed = []
        
        # ✅ DEBUG: Log job offers processing
        print(f"🔍 DEBUG: Processing {len(job_offers) if job_offers else 0} job offers")
        if job_offers:
            sample_job = job_offers[0]
            print(f"   Sample job fields: {list(sample_job.keys())}")
            print(f"   Sample job wage_gold: {sample_job.get('wage_gold')}")
        
        for job in job_offers[:50]:  # Top 50 offers
            processed.append({
                'country_id': job.get('country_id'),
                'country_name': job.get('country_name'),
                'wage': job.get('wage_original'),
                'wage_gold': job.get('wage_gold'),
                'salary_gold': job.get('wage_gold'),  # ✅ FIX: Add salary_gold for compatibility
                'currency_id': job.get('currency_id'),
                'currency_name': job.get('currency_name'),
                'job_title': job.get('job_title', 'Unknown'),
                'business_name': job.get('business_name', 'Unknown'),
                'business_id': job.get('country_id', 0)  # Fallback for compatibility
            })
        
        print(f"   ✅ Processed {len(processed)} job offers for reports")
        return processed
    
    def _process_market_offers(self, market_offers: List[Dict]) -> Dict[int, List[Dict]]:
        """Processes market offers to format expected by reports (dictionary grouped by item_id)"""
        processed = {}
        # Process ALL offers to show top 3 for each item type
        for offer in market_offers:
            item_id = offer.get('item_id')
            if item_id is not None:
                if item_id not in processed:
                    processed[item_id] = []
                
                processed[item_id].append({
                    'item_id': item_id,
                    'item_name': offer.get('item_name'),
                    'country_id': offer.get('country_id'),
                    'country': offer.get('country_name'),  # daily report oczekuje 'country'
                    'price_currency': offer.get('price_original'),
                    'price_gold': offer.get('price_gold'),
                    'currency_id': offer.get('currency_id'),
                    'currency_name': offer.get('currency_name'),
                    'amount': offer.get('quantity', 1)
                })
        return processed
    
    def _generate_report_from_db_data(self, data_bundle: Dict[str, Any], 
                                    sections: Dict[str, bool], report_type: str, 
                                    output_dir: str) -> Optional[str]:
        """
        Generates report using database data and centralized calculation services.
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
        
        # Przygotuj dane militarne i wojowników jeśli dostępne
        hits_data, wars_summary = self.db_manager.get_military_data() if sections.get('military', False) else ([], {})
        warriors_data = self.db_manager.get_warriors_data() if sections.get('warriors', False) else []
        
        # Przygotuj dane w formacie oczekiwanym przez generator
        summary_data = {
            'fetched_at': data_bundle.get('fetched_at'),
            'total_countries': len(data_bundle.get('countries', [])),
            'total_currencies': len(data_bundle.get('currencies_map', {})),
            'hits_data': hits_data,
            'wars_summary': wars_summary
        }
        
        # Załaduj dane historyczne dla porównań
        historical_data = load_historical_data()
        
        # Przygotuj top wojowników
        top_warriors = warriors_data[:10] if warriors_data else []
        
        # Przygotuj dane ekonomiczne w formacie oczekiwanym przez daily report
        if sections.get('economic', False):
            economic_summary = {
                'job_offers': data_bundle.get('best_jobs', []),
                'cheapest_items': data_bundle.get('cheapest_items', {}),
                'currency_rates': data_bundle.get('currency_rates', {}),
                'cheapest_items_all_countries': data_bundle.get('cheapest_items', {})
            }
            summary_data['economic_summary'] = economic_summary
        
        # Dodaj także dane do głównego poziomu dla innych komponentów
        summary_data.update({
            'best_jobs': data_bundle.get('best_jobs', []),
            'cheapest_items': data_bundle.get('cheapest_items', {}),
            'currency_rates': data_bundle.get('currency_rates', {}),
        })
        
        # Generuj raport używając istniejącego generatora
        return generate_report(
            summary_data=summary_data,
            historical_data=historical_data,
            top_warriors=top_warriors,
            items_map=data_bundle.get('items_map', {}),
            currencies_map=data_bundle.get('currencies_map', {}),
            country_map={c['country_id']: c['country_name'] for c in data_bundle.get('countries', [])},
            currency_codes_map=data_bundle.get('currency_codes_map', {}),
            gold_id=data_bundle.get('gold_id'),
            output_dir=output_dir,
            sections=sections
        )
    
    def _generate_html_report(self, data_bundle: Dict[str, Any], 
                            sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generuje dzienny raport HTML z danych z bazy"""
        
        # Przygotuj dane militarne i wojowników jeśli dostępne
        hits_data, wars_summary = self.db_manager.get_military_data() if sections.get('military', False) else ([], {})
        warriors_data = self.db_manager.get_warriors_data() if sections.get('warriors', False) else []
        
        # Przygotuj dane w formacie oczekiwanym przez generator
        summary_data = {
            'fetched_at': data_bundle.get('fetched_at'),
            'total_countries': len(data_bundle.get('countries', [])),
            'total_currencies': len(data_bundle.get('currencies_map', {})),
            'hits_data': hits_data,
            'wars_summary': wars_summary
        }
        
        # Załaduj dane historyczne dla porównań
        historical_data = load_historical_data()
        
        # Przygotuj top wojowników
        top_warriors = warriors_data[:10] if warriors_data else []
        
        # Przygotuj dane ekonomiczne w formacie oczekiwanym przez HTML report
        if sections.get('economic', False):
            economic_summary = {
                'job_offers': data_bundle.get('best_jobs', []),
                'cheapest_items': data_bundle.get('cheapest_items', {}),
                'currency_rates': data_bundle.get('currency_rates', {}),
                'cheapest_items_all_countries': data_bundle.get('cheapest_items', {})
            }
            summary_data['economic_summary'] = economic_summary
        
        # Dodaj także dane do głównego poziomu dla innych komponentów
        summary_data.update({
            'best_jobs': data_bundle.get('best_jobs', []),
            'cheapest_items': data_bundle.get('cheapest_items', {}),
            'currency_rates': data_bundle.get('currency_rates', {}),
        })
        
        return generate_html_report(
            summary_data=summary_data,
            historical_data=historical_data,
            top_warriors=top_warriors,
            items_map=data_bundle.get('items_map', {}),
            currencies_map=data_bundle.get('currencies_map', {}),
            country_map={c['country_id']: c['country_name'] for c in data_bundle.get('countries', [])},
            currency_codes_map=data_bundle.get('currency_codes_map', {}),
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
        """Generuje raport arbitrażu walutowego używając centralnych serwisów z danych z bazy"""
        
        currency_rates = data_bundle.get('currency_rates', {})
        currencies_map = data_bundle.get('currencies_map', {})
        
        if not currencies_map:
            print("❌ No currencies data available for arbitrage report")
            return None
            
        if not currency_rates:
            print("❌ No currency rates available for arbitrage report")
            return None
        
        print(f"✅ Using currency data: {len(currencies_map)} currencies, {len(currency_rates)} rates")
        
        # Użyj refaktoryzowanego CurrencyArbitrageAnalyzer
        analyzer = CurrencyArbitrageAnalyzer(min_profit_threshold=0.5)
        
        # Utwórz struktur danych dla analizatora z danych z bazy
        analyzer.currencies_map = currencies_map
        analyzer.currency_rates = currency_rates
        analyzer.gold_id = data_bundle.get('gold_id', 1)
        
        # Przygotuj eco_countries z danych z bazy
        countries = data_bundle.get('countries', [])
        analyzer.eco_countries = [
            {
                'country_id': c['country_id'],
                'country_name': c['country_name'],
                'currency_id': c['currency_id']
            }
            for c in countries
        ]
        
        # Znajdź okazje arbitrażowe używając danych z bazy (use_database=True, ale z już załadowanymi danymi)
        opportunities = analyzer.find_arbitrage_opportunities(use_database=False)  # False bo już mamy dane
        
        if opportunities:
            result = analyzer.generate_arbitrage_report(opportunities, "txt")
            if result and not result.startswith("❌"):
                return result
            else:
                print("❌ Failed to generate arbitrage report file")
                return None
        else:
            print("❌ No arbitrage opportunities found")
            return None
    
    def _generate_short_economic_report(self, data_bundle: Dict[str, Any], 
                                      output_dir: str) -> Optional[str]:
        """Generuje krótki raport ekonomiczny z danych z bazy"""
        
        # Sprawdź czy mamy potrzebne dane
        currencies_map = data_bundle.get('currencies_map', {})
        currency_rates = data_bundle.get('currency_rates', {})
        
        if not currencies_map:
            print("❌ No currencies data available for short economic report")
            return None
            
        if not currency_rates:
            print("❌ No currency rates available for short economic report")
            return None
        
        print(f"✅ Using economic data: {len(currencies_map)} currencies, {len(currency_rates)} rates")
        
        # Użyj istniejącego generatora - został już zrefaktoryzowany do używania DB
        try:
            return generate_short_economic_report(output_dir)
        except Exception as e:
            print(f"❌ Error generating short economic report: {e}")
            return None
    
    def _generate_google_sheets_report(self, data_bundle: Dict[str, Any], 
                                     sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generuje raport Google Sheets z danych z bazy"""
        
        try:
            from ...reports.factories.report_factory import ReportFactory
            from ...core.models.entities import ReportType
            
            # Przygotuj dane militarne i wojowników jeśli dostępne
            hits_data, wars_summary = self.db_manager.get_military_data() if sections.get('military', False) else ([], {})
            warriors_data = self.db_manager.get_warriors_data() if sections.get('warriors', False) else []
            
            # Przygotuj dane w formacie oczekiwanym przez Google Sheets exporter
            summary_data = {
                'fetched_at': data_bundle.get('fetched_at'),
                'total_countries': len(data_bundle.get('countries', [])),
                'total_currencies': len(data_bundle.get('currencies_map', {})),
                'hits_data': hits_data,
                'wars_summary': wars_summary,
                'report_type': 'google_sheets'
            }
            
            # Przygotuj top wojowników
            top_warriors = warriors_data[:10] if warriors_data else []
            summary_data['top_warriors'] = top_warriors
            
            # Przygotuj dane ekonomiczne
            if sections.get('economic', False):
                economic_summary = {
                    'job_offers': data_bundle.get('best_jobs', []),
                    'cheapest_items': data_bundle.get('cheapest_items', {}),
                    'currency_rates': data_bundle.get('currency_rates', {}),
                    'cheapest_items_all_countries': data_bundle.get('cheapest_items', {})
                }
                summary_data['economic_summary'] = economic_summary
            
            # Dodaj wszystkie dane ekonomiczne do głównego poziomu
            summary_data.update({
                'best_jobs': data_bundle.get('best_jobs', []),
                'cheapest_items': data_bundle.get('cheapest_items', {}),
                'currency_rates': data_bundle.get('currency_rates', {}),
                'items_map': data_bundle.get('items_map', {}),
                'currencies_map': data_bundle.get('currencies_map', {}),
                'currency_codes_map': data_bundle.get('currency_codes_map', {}),
                'gold_id': data_bundle.get('gold_id'),
                'countries': data_bundle.get('countries', []),
                'country_map': self._convert_countries_to_map(data_bundle.get('countries', [])),  # Convert countries list to map
                'regions_data': data_bundle.get('regions_data', []),
                'historical_data': self._load_historical_data(),  # Add historical data
            })
            
            # Utwórz generator Google Sheets
            generator = ReportFactory.create_generator(ReportType.GOOGLE_SHEETS, self.deps)
            
            # Generuj raport
            print("📊 Generating Google Sheets report using factory...")
            result = generator.generate(summary_data, sections, output_dir)
            
            if result:
                print(f"✅ Google Sheets report generated successfully: {result}")
                return result
            else:
                print("❌ Failed to generate Google Sheets report")
                return "❌ Failed to generate report"
                
        except Exception as e:
            print(f"❌ Error generating Google Sheets report: {e}")
            import traceback
            traceback.print_exc()
            return "❌ Failed to generate report"
    
    def _load_historical_data(self) -> Dict[str, Any]:
        """Load historical data for currency rate comparisons"""
        try:
            return load_historical_data()
        except Exception as e:
            print(f"⚠️ Could not load historical data: {e}")
            return {}
    
    def _convert_countries_to_map(self, countries_list: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Convert countries list to map format expected by EnhancedSheetsFormatter"""
        country_map = {}
        for country in countries_list:
            country_id = country.get('country_id')
            if country_id is not None:
                country_map[country_id] = {
                    'name': country.get('country_name'),
                    'currency_id': country.get('currency_id'),
                    'currency_name': country.get('currency_name')
                }
        return country_map
    
    def _fix_regions_country_names(self, regions_data: List[Dict[str, Any]], countries_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fix country names in regions_data by mapping country_id to actual country names"""
        if not regions_data or not countries_list:
            return regions_data
        
        # Create country_id -> country_name mapping
        country_id_to_name = {}
        for country in countries_list:
            country_id = country.get('country_id')
            country_name = country.get('country_name')
            if country_id and country_name:
                country_id_to_name[country_id] = country_name
        
        # Fix country names in regions_data
        fixed_regions = []
        fixed_count = 0
        for region in regions_data:
            region_copy = region.copy()
            country_id = region.get('country_id')
            
            # If country_name is Unknown or empty, try to fix it
            if region.get('country_name') in ['Unknown', '', None] and country_id in country_id_to_name:
                region_copy['country_name'] = country_id_to_name[country_id]
                fixed_count += 1
            
            fixed_regions.append(region_copy)
        
        if fixed_count > 0:
            print(f"✅ Fixed country names for {fixed_count} regions")
        
        return fixed_regions
    
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
