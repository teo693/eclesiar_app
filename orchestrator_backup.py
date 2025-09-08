from datetime import datetime, timedelta
import os
import sys
import time
from typing import Any, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import AUTH_TOKEN, GOLD_ID_FALLBACK, API_WORKERS_WAR, API_WORKERS_HITS
from api_client import fetch_data
from storage import (
    load_raw_api_output,
    save_raw_api_output,
    load_historical_data,
    save_historical_data,
    save_regions_data_to_storage,
    load_regions_data_from_storage,
)
from economy import (
    fetch_countries_and_currencies,
    build_currency_rates_map,
    compute_currency_extremes,
    fetch_best_jobs_from_all_countries,
    get_lowest_npc_wage_countries,
    fetch_cheapest_items_from_all_countries,
)
from regions import fetch_and_process_regions, compare_regions_with_history
from military import process_hits_data, build_wars_summary
from reporting import generate_report
from reporting_html import generate_html_report
from db import init_db, save_snapshot, save_currency_rates


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
    
    return raw_data_dump


class ConsoleProgress:
    def __init__(self) -> None:
        self.total: int = 0
        self.done: int = 0
        self.start_time: float = time.time()
        self._last_print: float = 0.0
        self._last_line_len: int = 0

    def add_tasks(self, count: int) -> None:
        if count <= 0:
            return
        self.total += count
        self._render(force=True)

    def advance(self, count: int = 1, note: str = "") -> None:
        self.done += max(0, count)
        self._render(note=note)

    def _format_eta(self) -> str:
        if self.done <= 0 or self.total <= 0:
            return "ETA --:--"
        elapsed = max(1e-6, time.time() - self.start_time)
        rate = self.done / elapsed
        remaining = max(0.0, (self.total - self.done) / max(1e-9, rate))
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        return f"ETA {mins:02d}:{secs:02d}"

    def _render(self, note: str = "", force: bool = False) -> None:
        now = time.time()
        if not force and (now - self._last_print) < 0.1 and self.done < self.total:
            return
        self._last_print = now
        total = max(1, self.total)
        ratio = min(1.0, self.done / total)
        percent = int(ratio * 100)
        bar_width = 30
        filled = int(ratio * bar_width)
        bar = "[" + "#" * filled + "-" * (bar_width - filled) + "]"
        eta = self._format_eta()
        msg = f" {percent:3d}% {bar} {self.done}/{self.total} {eta}"
        if note:
            msg += f" - {note}"
        line = "\r" + msg
        self._last_line_len = max(self._last_line_len, len(msg))
        pad = max(0, self._last_line_len - len(msg))
        sys.stdout.write(line + (" " * pad))
        sys.stdout.flush()

    def finish(self, final_note: str = "") -> None:
        if self.total > 0 and self.done < self.total:
            self.done = self.total
        self._render(note=final_note, force=True)
        sys.stdout.write("\n")
        sys.stdout.flush()


def run(sections: dict = None, report_type: str = "daily") -> None:
    if not AUTH_TOKEN:
        print("❌ Błąd: Token autoryzacyjny nie został załadowany z pliku .env.")
        return
    
    # Set default sections if not provided
    if sections is None:
        sections = {
            'military': True,
            'warriors': True, 
            'economic': True,
            'production': True
        }

    # Inicjalizacja bazy danych
    try:
        init_db()
        print("🗄️ Database initialized")
                except Exception as e:
        print(f"⚠️ Warning: database initialization failed: {e}")

    progress = ConsoleProgress()
    print(f"🚀 Starting process: fetching data for {report_type} report...")
    print("⚡ Always fetching fresh data from API (cache disabled)")

    # Use the new optimized data fetching function
    raw_data_dump = fetch_data_by_type(sections, report_type, progress)
    
    if not raw_data_dump:
        print("❌ Error: Cannot load data. Report will not be generated.")
        progress.finish(final_note="No data")
        return

    # Use the fetched data for report generation
    raw_data_from_file = raw_data_dump

    # Process the data and generate report
    historical_data = load_historical_data()
    today_key = datetime.now().strftime("%Y-%m-%d")

    try:
        # Get country map for processing
        country_map = {}
        eco_countries: Dict[int, Dict[str, Any]] = raw_data_from_file.get('eco_countries', {})
        if eco_countries:
            country_map = {cid: cinfo.get('name') for cid, cinfo in eco_countries.items() if cinfo.get('name')}
        else:
            # Fallback: try to get countries from /countries
            try:
                countries_payload = fetch_data("countries", "krajach")
                if countries_payload and countries_payload.get('data'):
                    country_map = {row.get('id'): row.get('name') for row in countries_payload['data'] if row.get('id') is not None}
            except Exception:
                pass

        # Process military data if available
        military_summary, top_warriors = process_hits_data(raw_data_from_file, country_map)
        print(f"Przetworzono dane wojskowe: {len(military_summary.get('damage_by_country', {}))} krajów")

        # Process economic data
        items_map = raw_data_from_file.get('items_map', {})
        currencies_map = raw_data_from_file.get('currencies_map', {})
        currency_codes_map = raw_data_from_file.get('currency_codes_map', {})
        economic_summary: Dict[str, Any] = {}
        
        if raw_data_from_file.get('currency_extremes'):
            try:
                most_expensive, cheapest = raw_data_from_file['currency_extremes']
            except Exception:
                most_expensive, cheapest = None, None
            economic_summary["most_expensive_currency"] = (
                {
                    "currency_id": most_expensive[0],
                    "currency_name": currencies_map.get(most_expensive[0], str(most_expensive[0])),
                    "currency_code": currency_codes_map.get(most_expensive[0], ""),
                    "gold_per_unit": most_expensive[1],
                }
                if most_expensive
                else None
            )
            economic_summary["cheapest_currency"] = (
                {
                    "currency_id": cheapest[0],
                    "currency_name": currencies_map.get(cheapest[0], str(cheapest[0])),
                    "currency_code": currency_codes_map.get(cheapest[0], ""),
                    "gold_per_unit": cheapest[1],
                }
                if cheapest
                else None
            )
        
        # Include currency rates for rendering
        if raw_data_from_file.get('currency_rates'):
            economic_summary["currency_rates"] = raw_data_from_file['currency_rates']
        
        # Add job offers data
        if raw_data_from_file.get('best_jobs'):
            economic_summary["best_jobs"] = raw_data_from_file['best_jobs']
            print(f"Załadowano {len(raw_data_from_file['best_jobs'])} najlepszych ofert pracy")
        
        # Add cheapest items data
        if raw_data_from_file.get('cheapest_items_all_countries'):
            economic_summary["cheapest_items_all_countries"] = raw_data_from_file['cheapest_items_all_countries']
            print(f"Loaded {len(raw_data_from_file['cheapest_items_all_countries'])} cheapest items from all countries")
            
        # Add NPC wages data
        if raw_data_from_file.get('currency_rates') and raw_data_from_file.get('eco_countries'):
            try:
                from economy import get_lowest_npc_wage_countries
                lowest_npc_wage = get_lowest_npc_wage_countries(
                    raw_data_from_file['currency_rates'], 
                    raw_data_from_file['eco_countries']
                )
                economic_summary["lowest_npc_wage"] = lowest_npc_wage
                print(f"Loaded NPC wages data for {len(lowest_npc_wage)} countries")
            except Exception as e:
                print(f"Error fetching lowest NPC wage data: {e}")
        
        # Add regions data
        if raw_data_from_file.get('regions_data'):
            economic_summary["regions_data"] = raw_data_from_file['regions_data']
            economic_summary["regions_summary"] = raw_data_from_file['regions_summary']
            print(f"Załadowano dane o {len(raw_data_from_file['regions_data'])} regionach z bonusami")

        # Process wars summary
        wars_summary = build_wars_summary(raw_data_from_file, country_map)
        print(f"Przetworzono podsumowanie wojen: {len(wars_summary.get('active_wars', []))} aktywnych wojen")
        
        fetched_at_for_report = raw_data_from_file.get('fetched_at')
        current_summary: Dict[str, Any] = {
            "military_summary": military_summary,
            "economic_summary": economic_summary,
            "wars_summary": wars_summary,
            "fetched_at": fetched_at_for_report,
            "top_warriors": top_warriors,
        }

        # Generate production data if needed
        if raw_data_from_file.get('regions_data') and (raw_data_from_file.get('eco_countries') or sections.get('production', False)):
            try:
                from production_analyzer_consolidated import ProductionAnalyzer
                analyzer = ProductionAnalyzer()
                production_data = analyzer.analyze_all_regions(raw_data_from_file['regions_data'])
                current_summary["production_data"] = production_data
                print(f"Generated productivity data for {len(production_data)} regions")
            except Exception as e:
                print(f"Error generating productivity data: {e}")
                current_summary["production_data"] = []

        # Generate report
        progress.add_tasks(1)
        report_file = generate_report(
            current_summary,
            historical_data,
            top_warriors,
            items_map,
            currencies_map,
            country_map,
            currency_codes_map,
            raw_data_from_file.get('gold_id', GOLD_ID_FALLBACK),
            "reports",
            sections,
        )
        progress.advance(note="Generating DOCX report")
        print(f"DOCX report generated: {report_file}")
        
        # Convert ProductionData objects to dictionaries for JSON serialization
        summary_for_save = current_summary.copy()
        if 'production_data' in summary_for_save:
            production_data = summary_for_save['production_data']
            if hasattr(production_data, '__iter__') and not isinstance(production_data, (str, bytes)):
                summary_for_save['production_data'] = [
                    {
                        'region_name': item.region_name,
                        'country_name': item.country_name,
                        'country_id': item.country_id,
                        'item_name': item.item_name,
                        'total_bonus': item.total_bonus,
                        'regional_bonus': item.regional_bonus,
                        'country_bonus': item.country_bonus,
                        'pollution': item.pollution,
                        'npc_wages': item.npc_wages,
                        'production_q1': item.production_q1,
                        'production_q2': item.production_q2,
                        'production_q3': item.production_q3,
                        'production_q4': item.production_q4,
                        'production_q5': item.production_q5,
                        'efficiency_score': item.efficiency_score,
                    } for item in production_data
                ]
        
        historical_data[today_key] = summary_for_save
        save_historical_data(historical_data)
        print(f"\n✅ DOCX report successfully generated: {report_file}")
        print(f"📊 Historical data saved for: {today_key}")
        progress.finish(final_note="Completed")
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        progress.finish(final_note="Przerwano z błędem")
        return


def run_html(output_dir: str = "reports", sections: dict = None) -> None:
    """Uruchamia orchestrator z generowaniem raportu HTML"""
    if not AUTH_TOKEN:
        print("❌ Błąd: Token autoryzacyjny nie został załadowany z pliku .env.")
        return
    
    # Ustaw domyślne sekcje jeśli nie podano
    if sections is None:
        sections = {
            'military': True,
            'warriors': True, 
            'economic': True,
            'production': True
        }

    # Inicjalizacja bazy danych
    try:
        init_db()
        print("🗄️ Database initialized")
    except Exception as e:
        print(f"⚠️ Warning: database initialization failed: {e}")

    progress = ConsoleProgress()
    print("🚀 Start procesu: pobieranie danych i generowanie raportu HTML...")
    print("⚡ Zawsze pobieram świeże dane z API (cache wyłączony)")

    # Use the new optimized data fetching function
    raw_data_dump = fetch_data_by_type(sections, "html", progress)
    
    if not raw_data_dump:
        print("❌ Error: Cannot load data. Report will not be generated.")
        progress.finish(final_note="No data")
            return

    # Use the fetched data for report generation
    raw_data_from_file = raw_data_dump

    # Process the data and generate HTML report
    historical_data = load_historical_data()
    today_key = datetime.now().strftime("%Y-%m-%d")

    try:
        # Get country map for processing
        country_map = {}
        eco_countries: Dict[int, Dict[str, Any]] = raw_data_from_file.get('eco_countries', {})
        if eco_countries:
            country_map = {cid: cinfo.get('name') for cid, cinfo in eco_countries.items() if cinfo.get('name')}
        else:
            # Fallback: try to get countries from /countries
            try:
                countries_payload = fetch_data("countries", "krajach")
                if countries_payload and countries_payload.get('data'):
                    country_map = {row.get('id'): row.get('name') for row in countries_payload['data'] if row.get('id') is not None}
            except Exception:
                pass

        # Process military data if available
        military_summary, top_warriors = process_hits_data(raw_data_from_file, country_map)
        print(f"Przetworzono dane wojskowe: {len(military_summary.get('damage_by_country', {}))} krajów")

        # Process economic data
        items_map = raw_data_from_file.get('items_map', {})
        currencies_map = raw_data_from_file.get('currencies_map', {})
        currency_codes_map = raw_data_from_file.get('currency_codes_map', {})
        economic_summary: Dict[str, Any] = {}
        
        if raw_data_from_file.get('currency_extremes'):
            try:
                most_expensive, cheapest = raw_data_from_file['currency_extremes']
            except Exception:
                most_expensive, cheapest = None, None
            economic_summary["most_expensive_currency"] = (
                {
                    "currency_id": most_expensive[0],
                    "currency_name": currencies_map.get(most_expensive[0], str(most_expensive[0])),
                    "currency_code": currency_codes_map.get(most_expensive[0], ""),
                    "gold_per_unit": most_expensive[1],
                }
                if most_expensive
                else None
            )
            economic_summary["cheapest_currency"] = (
                {
                    "currency_id": cheapest[0],
                    "currency_name": currencies_map.get(cheapest[0], str(cheapest[0])),
                    "currency_code": currency_codes_map.get(cheapest[0], ""),
                    "gold_per_unit": cheapest[1],
                }
                if cheapest
                else None
            )
        
        # Include currency rates for rendering
        if raw_data_from_file.get('currency_rates'):
            economic_summary["currency_rates"] = raw_data_from_file['currency_rates']
        
        # Add job offers data
        if raw_data_from_file.get('best_jobs'):
            economic_summary["best_jobs"] = raw_data_from_file['best_jobs']
            print(f"Załadowano {len(raw_data_from_file['best_jobs'])} najlepszych ofert pracy")
        
        # Add cheapest items data
        if raw_data_from_file.get('cheapest_items_all_countries'):
            economic_summary["cheapest_items_all_countries"] = raw_data_from_file['cheapest_items_all_countries']
            print(f"Loaded {len(raw_data_from_file['cheapest_items_all_countries'])} cheapest items from all countries")
            
        # Add NPC wages data
        if raw_data_from_file.get('currency_rates') and raw_data_from_file.get('eco_countries'):
            try:
                from economy import get_lowest_npc_wage_countries
                lowest_npc_wage = get_lowest_npc_wage_countries(
                    raw_data_from_file['currency_rates'], 
                    raw_data_from_file['eco_countries']
                )
                economic_summary["lowest_npc_wage"] = lowest_npc_wage
                print(f"Loaded NPC wages data for {len(lowest_npc_wage)} countries")
            except Exception as e:
                print(f"Error fetching lowest NPC wage data: {e}")
        
        # Add regions data
        if raw_data_from_file.get('regions_data'):
            economic_summary["regions_data"] = raw_data_from_file['regions_data']
            economic_summary["regions_summary"] = raw_data_from_file['regions_summary']
            print(f"Załadowano dane o {len(raw_data_from_file['regions_data'])} regionach z bonusami")

        # Process wars summary
        wars_summary = build_wars_summary(raw_data_from_file, country_map)
        print(f"Przetworzono podsumowanie wojen: {len(wars_summary.get('active_wars', []))} aktywnych wojen")
        
        fetched_at_for_report = raw_data_from_file.get('fetched_at')
        current_summary: Dict[str, Any] = {
            "military_summary": military_summary,
            "economic_summary": economic_summary,
            "wars_summary": wars_summary,
            "fetched_at": fetched_at_for_report,
            "top_warriors": top_warriors,
        }

        # Generate production data if needed
        if raw_data_from_file.get('regions_data') and (raw_data_from_file.get('eco_countries') or sections.get('production', False)):
            try:
                from production_analyzer_consolidated import ProductionAnalyzer
                analyzer = ProductionAnalyzer()
                production_data = analyzer.analyze_all_regions(raw_data_from_file['regions_data'])
                current_summary["production_data"] = production_data
                print(f"Generated productivity data for {len(production_data)} regions")
            except Exception as e:
                print(f"Error generating productivity data: {e}")
                current_summary["production_data"] = []

        # Generate HTML report
        progress.add_tasks(1)
        report_file = generate_html_report(
            current_summary,
            historical_data,
            top_warriors,
            items_map,
            currencies_map,
            country_map,
            currency_codes_map,
            raw_data_from_file.get('gold_id', GOLD_ID_FALLBACK),
            output_dir,
            sections,
        )
        progress.advance(note="Generowanie raportu HTML")
        print(f"HTML report generated: {report_file}")
        
        # Convert ProductionData objects to dictionaries for JSON serialization
        summary_for_save = current_summary.copy()
        if 'production_data' in summary_for_save:
            production_data = summary_for_save['production_data']
            if hasattr(production_data, '__iter__') and not isinstance(production_data, (str, bytes)):
                summary_for_save['production_data'] = [
                    {
                        'region_name': item.region_name,
                        'country_name': item.country_name,
                        'country_id': item.country_id,
                        'item_name': item.item_name,
                        'total_bonus': item.total_bonus,
                        'regional_bonus': item.regional_bonus,
                        'country_bonus': item.country_bonus,
                        'pollution': item.pollution,
                        'npc_wages': item.npc_wages,
                        'production_q1': item.production_q1,
                        'production_q2': item.production_q2,
                        'production_q3': item.production_q3,
                        'production_q4': item.production_q4,
                        'production_q5': item.production_q5,
                        'efficiency_score': item.efficiency_score,
                    } for item in production_data
                ]
        
        historical_data[today_key] = summary_for_save
        save_historical_data(historical_data)
        print(f"\n✅ HTML report successfully generated: {report_file}")
        print(f"📊 Historical data saved for: {today_key}")
        progress.finish(final_note="Completed")
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        progress.finish(final_note="Przerwano z błędem")
        return


if __name__ == "__main__":
    run_html()
