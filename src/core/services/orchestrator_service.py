from datetime import datetime, timedelta
import os
import sys
import time
from typing import Any, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings.base import AUTH_TOKEN, GOLD_ID_FALLBACK, API_WORKERS_WAR, API_WORKERS_HITS
from src.data.api.client import fetch_data
from src.data.storage.cache import (
    load_raw_api_output,
    save_raw_api_output,
    load_historical_data,
    save_historical_data,
    save_regions_data_to_storage,
    load_regions_data_from_storage,
)
from src.core.services.economy_service import (
    fetch_countries_and_currencies,
    build_currency_rates_map,
    compute_currency_extremes,
    fetch_best_jobs_from_all_countries,
    get_lowest_npc_wage_countries,
    fetch_cheapest_items_from_all_countries,
)
from src.core.services.regions_service import fetch_and_process_regions, compare_regions_with_history
from src.core.services.military_service import process_hits_data, build_wars_summary
from src.reports.generators.daily_report import generate_report
from src.reports.generators.html_report import generate_html_report
from src.data.database.models import init_db, save_snapshot, save_currency_rates


def fetch_data_by_type(sections: dict, report_type: str = "daily", progress = None) -> Dict[str, Any]:
    """
    Fetch data from API based on report type and sections.
    Returns only the data needed for the specific report.
    """
    if progress is None:
        # Create a simple progress object
        class SimpleProgress:
            def __init__(self):
                self.total = 0
                self.done = 0
            def add_tasks(self, count):
                self.total += count
            def advance(self, note=""):
                self.done += 1
                print(f"Progress: {self.done}/{self.total} - {note}")
            def finish(self, note=""):
                print(f"Completed: {note}")
        progress = SimpleProgress()
    
    # Determine what data to fetch based on report type
    fetch_military = report_type in ["daily", "full"] and (sections.get('military', True) or sections.get('warriors', True))
    fetch_economic = report_type in ["daily", "economic", "full"] and sections.get('economic', True)
    fetch_production = report_type in ["daily", "production", "full"] and sections.get('production', True)
    
    print(f"📊 Fetching data: military={fetch_military}, economic={fetch_economic}, production={fetch_production}")
    raw_data_dump: Dict[str, Any] = {}
    
    try:
        # Military data (wars, rounds, hits) - only if needed
        if fetch_military:
            print("⚔️ Fetching military data...")
            progress.add_tasks(1)
            raw_data_dump['wars'] = fetch_data("wars", "wojnach")
            try:
                if raw_data_dump['wars']:
                    save_snapshot("wars", raw_data_dump['wars'])
            except Exception:
                pass
            progress.advance(note="Lista wojen")
            
            # Continue with military data fetching if wars exist
            if raw_data_dump['wars'] and raw_data_dump['wars'].get('data'):
                # Fetch rounds and hits (simplified version)
                yesterday = datetime.now() - timedelta(days=1)
                war_ids: List[int] = [w.get('id') for w in raw_data_dump['wars']['data'] if w.get('id') is not None]

                # Limit wars for performance
                max_wars_to_analyze = int(os.getenv("MAX_WARS_TO_ANALYZE", "20"))
                if len(war_ids) > max_wars_to_analyze:
                    print(f"Ograniczam analizę do {max_wars_to_analyze} wojen z {len(war_ids)} dostępnych")
                    war_ids = war_ids[:max_wars_to_analyze]

                # Fetch hits for recent rounds (simplified)
                hits_result: Dict[str, Any] = {}
                max_workers_hits = int(os.getenv("API_WORKERS_HITS", "16"))

                def fetch_hits(round_id: int) -> Tuple[int, Any]:
                    payload = fetch_data(f"war/round/hits?war_round_id={round_id}", f"uderzeniach rundy {round_id}")
                    try:
                        if payload:
                            save_snapshot("war/round/hits", {"round_id": round_id, "data": payload})
                    except Exception:
                        pass
                    return round_id, payload

                # For simplicity, just fetch a few recent rounds
                if war_ids:
                    with ThreadPoolExecutor(max_workers=max_workers_hits) as executor:
                        # Just fetch first few wars for performance
                        sample_war_ids = war_ids[:3]
                        futures = {executor.submit(fetch_hits, rid): rid for rid in sample_war_ids}
                        progress.add_tasks(len(futures))
                        for fut in as_completed(futures):
                            try:
                                rid, payload = fut.result()
                                hits_result[str(rid)] = payload
                                progress.advance(note=f"Uderzenia runda {rid}")
                            except Exception:
                                progress.advance(note="Błąd uderzeń")

                raw_data_dump['hits'] = hits_result
            else:
                raw_data_dump['hits'] = {}
        else:
            print("⚔️ Skipping military data (not needed for this report)")
            raw_data_dump['wars'] = {}
            raw_data_dump['hits'] = {}

        # Economic data - only if needed
        if fetch_economic or fetch_production:
            print("💰 Fetching economic data...")
            progress.add_tasks(1)
            eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
            progress.advance(note="Kraje i waluty")
            
            if not eco_countries or not currencies_map:
                print("No economic data - skipping further fetching")
                raw_data_dump['eco_countries'] = {}
                raw_data_dump['currencies_map'] = {}
                raw_data_dump['currency_codes_map'] = {}
                raw_data_dump['gold_id'] = GOLD_ID_FALLBACK
                return raw_data_dump
                
            raw_data_dump['eco_countries'] = eco_countries
            raw_data_dump['currencies_map'] = currencies_map
            raw_data_dump['currency_codes_map'] = currency_codes_map
            raw_data_dump['gold_id'] = gold_id or GOLD_ID_FALLBACK
                
            try:
                save_snapshot("countries_and_currencies", {
                    "eco_countries": eco_countries,
                    "currencies_map": currencies_map,
                    "currency_codes_map": currency_codes_map,
                    "gold_id": raw_data_dump['gold_id'],
                })
            except Exception:
                pass
                
            # Fetch additional economic data only if needed
            if fetch_economic:
                # Currency rates
                if not raw_data_dump.get('currency_rates') or os.getenv("REFRESH_RATES", "0") == "1":
                    progress.add_tasks(1)
                    raw_data_dump['currency_rates'] = build_currency_rates_map(currencies_map, raw_data_dump['gold_id'])
                    progress.advance(note="Kursy walut")
                    try:
                        save_snapshot("currency_rates", raw_data_dump['currency_rates'])
                        save_currency_rates(raw_data_dump['currency_rates'])
                        print(f"Zaktualizowano kursy walut dla {len(raw_data_dump['currency_rates'])} walut")
                    except Exception:
                        pass
                
                # Best jobs
                progress.add_tasks(1)
                raw_data_dump['best_jobs'] = fetch_best_jobs_from_all_countries(
                    eco_countries, raw_data_dump.get('currency_rates', {}), raw_data_dump['gold_id']
                )
                progress.advance(note="Ekonomia: najlepsze oferty pracy")
                
                # Cheapest items
                progress.add_tasks(1)
                if not raw_data_dump.get('items_map'):
                    from economy import fetch_items_by_type
                    raw_data_dump['items_map'] = fetch_items_by_type(report_type)
                    print(f"DEBUG: Pobrano {len(raw_data_dump['items_map'])} towarów dla raportu typu: {report_type}")
                
                if eco_countries:
                    print(f"Pobieranie najtańszych towarów dla {len(eco_countries)} krajów i {len(raw_data_dump.get('items_map', {}))} towarów...")
                    raw_data_dump['cheapest_items_all_countries'] = fetch_cheapest_items_from_all_countries(
                        eco_countries, raw_data_dump.get('items_map', {}), raw_data_dump.get('currency_rates', {}), raw_data_dump['gold_id']
                    )
                    print(f"Pobrano {len(raw_data_dump['cheapest_items_all_countries'])} najtańszych towarów")
                    progress.advance(note="Ekonomia: najtańsze towary ze wszystkich krajów")
                else:
                    print("Brak krajów do pobrania najtańszych towarów")
                    raw_data_dump['cheapest_items_all_countries'] = {}
                    progress.advance(note="Ekonomia: brak krajów")
                
                # Currency extremes
                progress.add_tasks(1)
                raw_data_dump['currency_extremes'] = compute_currency_extremes(
                    raw_data_dump.get('currency_rates', {}), currencies_map, raw_data_dump['gold_id']
                )
                progress.advance(note="Ekonomia: kursy skrajne")
                
            # Regions data - only if production analysis is needed
            if fetch_production:
                progress.add_tasks(1)
                regions_data, regions_summary = fetch_and_process_regions(eco_countries)
                if regions_data:
                    raw_data_dump['regions_data'] = regions_data
                    raw_data_dump['regions_summary'] = regions_summary
                    print(f"Fetched data for {len(regions_data)} regions with bonuses")
                    try:
                        save_regions_data_to_storage(regions_data, regions_summary)
                    except Exception as e:
                        print(f"Error saving region data to database: {e}")
                else:
                    print("No region data - using empty cache")
                    raw_data_dump['regions_data'] = []
                    raw_data_dump['regions_summary'] = {}
                progress.advance(note="Ekonomia: regiony z bonusami")
        else:
            print("💰 Skipping economic data (not needed for this report)")
            raw_data_dump['eco_countries'] = {}
            raw_data_dump['currencies_map'] = {}
            raw_data_dump['currency_codes_map'] = {}
            raw_data_dump['gold_id'] = GOLD_ID_FALLBACK

        raw_data_dump['fetched_at'] = datetime.now().isoformat()
        save_raw_api_output(raw_data_dump)
        
    except Exception as e:
        print(f"❌ Error occurred while fetching data: {e}")
        import traceback
        traceback.print_exc()
        progress.finish(final_note="Przerwano z błędem")
        return {}
    
    progress.finish(final_note="Dane pobrane")
    return raw_data_dump


def run(sections: dict = None, report_type: str = "daily") -> None:
    """
    Main orchestrator function that coordinates data fetching and report generation.
    """
    if sections is None:
        sections = {
            'military': True,
            'warriors': True, 
            'economic': True,
            'production': True
        }
    
    print(f"🚀 Starting process: fetching data and generating report...")
    print(f"⚡ Always fetching fresh data from API (cache disabled)")
    
    # Initialize database
    try:
        init_db()
        print("🗄️ Database initialized")
    except Exception as e:
        print(f"⚠️ Warning: database initialization failed: {e}")

    progress = ConsoleProgress()
    
    # Fetch data based on report type
    raw_data_dump = fetch_data_by_type(sections, report_type, progress)
    
    if not raw_data_dump:
        print("❌ Error: Cannot load data. Report will not be generated.")
        progress.finish(final_note="No data")
        return

    # Load historical data for comparison
    historical_data = load_historical_data()
    
    # Generate report
    report_file = generate_report(
        raw_data_dump,
        historical_data,
        {},  # top_warriors - empty for now
        raw_data_dump.get('items_map', {}),
        raw_data_dump.get('currencies_map', {}),
        raw_data_dump.get('eco_countries', {}),
        raw_data_dump.get('currency_codes_map', {}),
        raw_data_dump.get('gold_id'),
        "reports",
        sections,
    )
    
    if report_file:
        print(f"✅ DOCX report successfully generated: {report_file}")
    else:
        print("❌ Failed to generate report")


class ConsoleProgress:
    def __init__(self):
        self.total = 0
        self.done = 0
    
    def add_tasks(self, count):
        self.total += count
    
    def advance(self, note=""):
        self.done += 1
        print(f"Progress: {self.done}/{self.total} - {note}")
    
    def finish(self, note=""):
        print(f"Completed: {note}")


if __name__ == "__main__":
    run()
