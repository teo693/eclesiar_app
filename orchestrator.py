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


def run(sections: dict = None) -> None:
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
        print("🗄️ Baza danych zainicjalizowana")
    except Exception as e:
        print(f"⚠️ Uwaga: inicjalizacja bazy danych nie powiodła się: {e}")

    progress = ConsoleProgress()
    print("🚀 Start procesu: pobieranie danych i generowanie raportu...")
    print("⚡ Zawsze pobieram świeże dane z API (cache wyłączony)")

    # Zawsze pobieraj świeże dane z API - cache wyłączony
    print("Pobieram świeże dane z API...")
    raw_data_dump: Dict[str, Any] = {}
    try:
        # Pobranie listy wojen
        progress.add_tasks(1)
        raw_data_dump['wars'] = fetch_data("wars", "wojnach")
        try:
            if raw_data_dump['wars']:
                save_snapshot("wars", raw_data_dump['wars'])
        except Exception:
            pass
        progress.advance(note="Lista wojen")
        
        # Sprawdź czy mamy dane o wojnach w cache
        if not raw_data_dump['wars'] or not raw_data_dump['wars'].get('data'):
            print("Brak danych o wojnach - pomijam pobieranie rund i uderzeń")
            raw_data_dump['hits'] = {}
            progress.advance(note="Brak wojen - pominięto")
            return

        # Równoległe pobieranie rund i uderzeń (ograniczona liczba wątków)
        hits_result: Dict[str, Any] = {}
        if raw_data_dump['wars'] and raw_data_dump['wars'].get('data'):
                yesterday = datetime.now() - timedelta(days=1)
                war_ids: List[int] = [w.get('id') for w in raw_data_dump['wars']['data'] if w.get('id') is not None]

                # Ogranicz liczbę wojen do analizy dla lepszej wydajności
                max_wars_to_analyze = int(os.getenv("MAX_WARS_TO_ANALYZE", "20"))
                if len(war_ids) > max_wars_to_analyze:
                    print(f"Ograniczam analizę do {max_wars_to_analyze} wojen z {len(war_ids)} dostępnych")
                    war_ids = war_ids[:max_wars_to_analyze]

                max_workers = int(os.getenv("API_WORKERS_WAR", "12"))

                # Etap 1: pobierz rundy dla wszystkich wojen równolegle
                def fetch_rounds(war_id: int) -> Tuple[int, List[Dict[str, Any]]]:
                    rounds_payload = fetch_data(f"war/rounds?war_id={war_id}", f"rundach wojny {war_id}")
                    rounds = (rounds_payload or {}).get('data') or []
                    try:
                        if rounds_payload:
                            save_snapshot("war/rounds", {"war_id": war_id, "data": rounds_payload})
                    except Exception:
                        pass
                    return war_id, rounds

                rounds_per_war: Dict[int, List[Dict[str, Any]]] = {}
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(fetch_rounds, wid): wid for wid in war_ids}
                    progress.add_tasks(len(futures))
                    for fut in as_completed(futures):
                        try:
                            wid, rounds = fut.result()
                            rounds_per_war[wid] = rounds
                            progress.advance(note=f"Rundy wojny {wid}")
                        except Exception:
                            progress.advance(note="Błąd rundy")

                # Etap 2: z rund po wczoraj pobierz uderzenia równolegle
                def should_fetch_round(r: Dict[str, Any]) -> bool:
                    end_date_str = r.get('end_date')
                    if not end_date_str:
                        return False
                    try:
                        end_date = datetime.fromisoformat(str(end_date_str).replace('Z', '+00:00'))
                    except Exception:
                        return False
                    # Ogranicz do rund z ostatnich 24h dla lepszej wydajności
                    return end_date > yesterday and end_date > (datetime.now() - timedelta(hours=24))

                round_ids_to_fetch: List[int] = []
                for rounds in rounds_per_war.values():
                    for r in rounds:
                        if should_fetch_round(r):
                            rid = r.get('id')
                            if isinstance(rid, int):
                                round_ids_to_fetch.append(rid)

                def fetch_hits(round_id: int) -> Tuple[int, Any]:
                    payload = fetch_data(f"war/round/hits?war_round_id={round_id}", f"uderzeniach rundy {round_id}")
                    try:
                        if payload:
                            save_snapshot("war/round/hits", {"round_id": round_id, "data": payload})
                    except Exception:
                        pass
                    return round_id, payload

                if round_ids_to_fetch:
                    max_workers_hits = int(os.getenv("API_WORKERS_HITS", "16"))
                    with ThreadPoolExecutor(max_workers=max_workers_hits) as executor:
                        futures = {executor.submit(fetch_hits, rid): rid for rid in round_ids_to_fetch}
                        progress.add_tasks(len(futures))
                        for fut in as_completed(futures):
                            try:
                                rid, payload = fut.result()
                                hits_result[str(rid)] = payload
                                progress.advance(note=f"Uderzenia runda {rid}")
                            except Exception:
                                progress.advance(note="Błąd uderzeń")

        if hits_result:
            raw_data_dump['hits'] = hits_result
            print(f"Pobrano dane o {len(hits_result)} rundach z uderzeniami")
        else:
            print("Brak danych o uderzeniach - używam pustego cache")
            raw_data_dump['hits'] = {}

        # Ekonomia
        progress.add_tasks(1)
        eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
        progress.advance(note="Kraje i waluty")
        
        # Sprawdź czy mamy dane ekonomiczne
        if not eco_countries or not currencies_map:
                print("Brak danych ekonomicznych - pomijam dalsze pobieranie")
                raw_data_dump['eco_countries'] = {}
                raw_data_dump['currencies_map'] = {}
                raw_data_dump['currency_codes_map'] = {}
                raw_data_dump['gold_id'] = GOLD_ID_FALLBACK
                return
                
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
        if eco_countries:
                # Usunięto pobieranie items_map - nie jest potrzebne do raportów
                # raw_data_dump['items_map'] = {}  # Pusty słownik zamiast pobierania
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
                else:
                    print("Używam cache kursów walut")
                # Usunięto obliczanie skrajności cen - nie jest potrzebne do raportów
                # raw_data_dump['cheapest_by_item'] = {}
                # raw_data_dump['expensive_by_item'] = {}
                
                # Pobierz najlepsze oferty pracy ze wszystkich krajów
                progress.add_tasks(1)
                raw_data_dump['best_jobs'] = fetch_best_jobs_from_all_countries(
                    eco_countries, raw_data_dump.get('currency_rates', {}), raw_data_dump['gold_id']
                )
                progress.advance(note="Ekonomia: najlepsze oferty pracy")
                
                # Pobierz najtańsze towary ze wszystkich krajów
                progress.add_tasks(1)
                # Pobierz mapę towarów jeśli nie ma w cache
                if not raw_data_dump.get('items_map'):
                    from economy import fetch_all_items
                    raw_data_dump['items_map'] = fetch_all_items()
                    print(f"DEBUG: Pobrano {len(raw_data_dump['items_map'])} towarów")
                else:
                    print(f"DEBUG: Używam cache z {len(raw_data_dump['items_map'])} towarami")
                
                # Użyj wszystkich krajów z eco_countries (już walidowanych podczas pobierania)
                valid_countries = eco_countries
                print(f"DEBUG: eco_countries count: {len(eco_countries) if eco_countries else 0}")
                
                if valid_countries:
                    print(f"Pobieranie najtańszych towarów dla {len(valid_countries)} krajów i {len(raw_data_dump.get('items_map', {}))} towarów...")
                    raw_data_dump['cheapest_items_all_countries'] = fetch_cheapest_items_from_all_countries(
                        valid_countries, raw_data_dump.get('items_map', {}), raw_data_dump.get('currency_rates', {}), raw_data_dump['gold_id']
                    )
                    print(f"Pobrano {len(raw_data_dump['cheapest_items_all_countries'])} najtańszych towarów")
                    progress.advance(note="Ekonomia: najtańsze towary ze wszystkich krajów")
                else:
                    print("Brak krajów do pobrania najtańszych towarów")
                    raw_data_dump['cheapest_items_all_countries'] = {}
                    progress.advance(note="Ekonomia: brak krajów")
                
                progress.add_tasks(1)
                raw_data_dump['currency_extremes'] = compute_currency_extremes(
                    raw_data_dump.get('currency_rates', {}), currencies_map, raw_data_dump['gold_id']
                )
                progress.advance(note="Ekonomia: kursy skrajne")
                
                # Pobierz dane o regionach z bonusami
                progress.add_tasks(1)
                regions_data, regions_summary = fetch_and_process_regions(eco_countries)
                if regions_data:
                    raw_data_dump['regions_data'] = regions_data
                    raw_data_dump['regions_summary'] = regions_summary
                    print(f"Pobrano dane o {len(regions_data)} regionach z bonusami")
                    try:
                        save_regions_data_to_storage(regions_data, regions_summary)
                    except Exception as e:
                        print(f"Błąd podczas zapisu danych o regionach do bazy: {e}")
                else:
                    print("Brak danych o regionach - używam pustego cache")
                    raw_data_dump['regions_data'] = []
                    raw_data_dump['regions_summary'] = {}
                progress.advance(note="Ekonomia: regiony z bonusami")

        raw_data_dump['fetched_at'] = datetime.now().isoformat()
        save_raw_api_output(raw_data_dump)
        raw_data_from_file = raw_data_dump
    except Exception as e:
        print(f"❌ Wystąpił błąd przy pobieraniu danych: {e}")
        import traceback
        traceback.print_exc()
        progress.finish(final_note="Przerwano z błędem")
        return
    # Użyj świeżo pobranych danych
    raw_data_from_file = raw_data_dump

    # Sprawdź czy dane zostały pomyślnie pobrane
    if not raw_data_dump:
        print("❌ Błąd: Nie można wczytać danych. Raport nie zostanie wygenerowany.")
        progress.finish(final_note="Brak danych")
        return

    # Uzupełnij brakujące dane ekonomiczne jeśli potrzeba
    try:
        eco_countries_cache = raw_data_from_file.get('eco_countries') or {}
        currencies_map_cache = raw_data_from_file.get('currencies_map') or {}
        currency_codes_map_cache = raw_data_from_file.get('currency_codes_map') or {}
        gold_id_cache = raw_data_from_file.get('gold_id') or GOLD_ID_FALLBACK
        items_map_cache = raw_data_from_file.get('items_map') or {}
        currency_rates_cache = raw_data_from_file.get('currency_rates') or {}

        # Jeśli wymuszono odświeżenie kursów/ekonomii, odśwież także mapy walut i GOLD ID
        if os.getenv("REFRESH_RATES", "0") == "1" or os.getenv("RECALC_ECONOMY", "0") == "1":
            try:
                eco_countries_cache, currencies_map_cache, currency_codes_map_cache, detected_gold_id = fetch_countries_and_currencies()
                if detected_gold_id is not None and detected_gold_id >= 0:
                    gold_id_cache = detected_gold_id
                # Zapisz odświeżone mapy w cache w pamięci
                raw_data_from_file['eco_countries'] = eco_countries_cache
                raw_data_from_file['currencies_map'] = currencies_map_cache
                raw_data_from_file['currency_codes_map'] = currency_codes_map_cache
                raw_data_from_file['gold_id'] = gold_id_cache
            except Exception:
                pass

        # Usunięto need_items_extremes - nie jest potrzebne do raportów
        need_items_extremes = False
        
        need_jobs_data = (
            bool(eco_countries_cache)
            and bool(currency_rates_cache)
            and not raw_data_from_file.get('best_jobs')
        )
        
        # Sprawdź czy potrzebne są dane o najtańszych towarach
        need_cheapest_items_all = (
            bool(eco_countries_cache)
            and bool(currency_rates_cache)
            and bool(items_map_cache)
            and not raw_data_from_file.get('cheapest_items_all_countries')
        )
        print(f"DEBUG: need_cheapest_items_all = {need_cheapest_items_all}")
        print(f"DEBUG: eco_countries_cache: {bool(eco_countries_cache)}, currency_rates_cache: {bool(currency_rates_cache)}, items_map_cache: {bool(items_map_cache)}, cheapest_items_exists: {bool(raw_data_from_file.get('cheapest_items_all_countries'))}")
        need_currency_extremes = (
            bool(currency_rates_cache)
            and bool(currencies_map_cache)
            and not raw_data_from_file.get('currency_extremes')
        )
        
        need_regions_data = (
            bool(eco_countries_cache)
            and (
                os.getenv("RECALC_ECONOMY", "0") == "1"
                or not raw_data_from_file.get('regions_data')
            )
        )

        # Jeżeli wymuszono odświeżenie kursów – przelicz kursy walut i skrajności niezależnie od powyższych flag
        if os.getenv("REFRESH_RATES", "0") == "1" and currencies_map_cache and (gold_id_cache is not None):
            try:
                currency_rates_cache = build_currency_rates_map(currencies_map_cache, gold_id_cache)
                raw_data_from_file['currency_rates'] = currency_rates_cache
                # Po zmianie kursów trzeba też odświeżyć skrajności
                need_currency_extremes = True
                # Usunięto need_items_extremes - nie jest potrzebne do raportów
                try:
                    save_snapshot("currency_rates", raw_data_from_file['currency_rates'])
                    save_currency_rates(raw_data_from_file['currency_rates'])
                except Exception:
                    pass
            except Exception:
                pass

        # Usunięto need_items_extremes - nie jest potrzebne do raportów
        # if need_items_extremes: ...
        
        if need_jobs_data:
            progress.add_tasks(1)
            raw_data_from_file['best_jobs'] = fetch_best_jobs_from_all_countries(
                eco_countries_cache, currency_rates_cache, gold_id_cache
            )
            progress.advance(note="Ekonomia (cache): oferty pracy uzupełnione")
        
        if need_cheapest_items_all:
            progress.add_tasks(1)
            # Pobierz mapę towarów jeśli nie ma w cache
            if not items_map_cache:
                from economy import fetch_all_items
                items_map_cache = fetch_all_items()
                raw_data_from_file['items_map'] = items_map_cache
            
            # Sprawdź czy kraje istnieją w API przed pobieraniem danych
            valid_countries_cache = {}
            for country_id, country_info in eco_countries_cache.items():
                try:
                    # Sprawdź czy kraj istnieje w API
                    test_url = f"country/{country_id}"
                    test_response = fetch_data(test_url, f"test kraju {country_id}")
                    if test_response is not None and test_response.get("code") == 200:
                        valid_countries_cache[country_id] = country_info
                    else:
                        print(f"Kraj {country_id} ({country_info.get('name', 'Unknown')}) nie istnieje w API - pomijam")
                except Exception as e:
                    print(f"Błąd podczas sprawdzania kraju {country_id}: {e}")
                    continue
            
            if valid_countries_cache:
                raw_data_from_file['cheapest_items_all_countries'] = fetch_cheapest_items_from_all_countries(
                    valid_countries_cache, items_map_cache, currency_rates_cache, gold_id_cache
                )
                progress.advance(note="Ekonomia (cache): najtańsze towary uzupełnione")
            else:
                print("Brak ważnych krajów do pobrania najtańszych towarów")
                raw_data_from_file['cheapest_items_all_countries'] = {}
                progress.advance(note="Ekonomia (cache): brak ważnych krajów")

        if need_currency_extremes:
            progress.add_tasks(1)
            raw_data_from_file['currency_extremes'] = compute_currency_extremes(
                currency_rates_cache, currencies_map_cache, gold_id_cache
            )
            progress.advance(note="Ekonomia (cache): kursy skrajne uzupełnione")
        
        if need_regions_data:
            progress.add_tasks(1)
            # Try to load from cache first
            regions_data, regions_summary = load_regions_data_from_storage()
            if not regions_data:
                # If no cached data, fetch fresh data
                print("Brak danych o regionach w cache - pobieranie świeżych danych...")
                regions_data, regions_summary = fetch_and_process_regions(eco_countries_cache)
                if regions_data:
                    try:
                        save_regions_data_to_storage(regions_data, regions_summary)
                    except Exception as e:
                        print(f"Błąd podczas zapisu danych o regionach do bazy (cache): {e}")
            
            if regions_data:
                raw_data_from_file['regions_data'] = regions_data
                raw_data_from_file['regions_summary'] = regions_summary
            progress.advance(note="Ekonomia (cache): regiony z bonusami uzupełnione")

        if need_currency_extremes or need_regions_data or need_cheapest_items_all:
            save_raw_api_output(raw_data_from_file)
            print("Zaktualizowano cache z nowymi danymi")
    except Exception as e:
        # Brakujące dane ekonomiczne w cache to nie-krytyczny błąd – kontynuujemy generowanie raportu
        print(f"⚠️ Uwaga: problem z cache ekonomicznym: {e}")
        pass

    historical_data = load_historical_data()
    today_key = datetime.now().strftime("%Y-%m-%d")

    try:
        # Bazuj na eco_countries aby uniknąć dodatkowego requestu /countries
        country_map = {}
        eco_countries: Dict[int, Dict[str, Any]] = raw_data_from_file.get('eco_countries', {})
        if eco_countries:
            country_map = {cid: cinfo.get('name') for cid, cinfo in eco_countries.items() if cinfo.get('name')}
        else:
            # Fallback: spróbuj pobrać listę krajów z /countries
            try:
                countries_payload = fetch_data("countries", "krajach")
                if countries_payload and countries_payload.get('data'):
                    country_map = {row.get('id'): row.get('name') for row in countries_payload['data'] if row.get('id') is not None}
            except Exception:
                pass

        # Przetwarzanie danych wojskowych
        progress.add_tasks(1)
        military_summary, top_warriors = process_hits_data(raw_data_from_file, country_map)
        progress.advance(note="Przetwarzanie uderzeń")
        print(f"Przetworzono dane wojskowe: {len(military_summary.get('damage_by_country', {}))} krajów")

        # items_map jest potrzebne do mapowania nazw towarów w sekcji "Najtańsze towary"
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
        # Usunięto cheapest_by_item i expensive_by_item - nie są potrzebne do raportów
        # economic_summary["cheapest_by_item"] = {}
        # economic_summary["most_expensive_by_item"] = {}
        # Include currency rates for rendering a sorted rates table in the report
        if raw_data_from_file.get('currency_rates'):
            economic_summary["currency_rates"] = raw_data_from_file['currency_rates']
        
        # Dodaj dane o ofertach pracy
        if raw_data_from_file.get('best_jobs'):
            economic_summary["best_jobs"] = raw_data_from_file['best_jobs']
            print(f"Załadowano {len(raw_data_from_file['best_jobs'])} najlepszych ofert pracy")
        
        # Dodaj dane o najtańszych towarach ze wszystkich krajów
        if raw_data_from_file.get('cheapest_items_all_countries'):
            economic_summary["cheapest_items_all_countries"] = raw_data_from_file['cheapest_items_all_countries']
            print(f"Loaded {len(raw_data_from_file['cheapest_items_all_countries'])} cheapest items from all countries")
            
        # Dodaj dane o najniższych NPC wage
        if raw_data_from_file.get('currency_rates') and raw_data_from_file.get('eco_countries'):
            try:
                lowest_npc_wage = get_lowest_npc_wage_countries(
                    raw_data_from_file['currency_rates'], 
                    raw_data_from_file['eco_countries']
                )
                economic_summary["lowest_npc_wage"] = lowest_npc_wage
                print(f"Loaded NPC wages data for {len(lowest_npc_wage)} countries")
            except Exception as e:
                print(f"Błąd podczas pobierania danych o najniższych NPC wage: {e}")
        
        # Dodaj dane o regionach z bonusami
        if raw_data_from_file.get('regions_data'):
            economic_summary["regions_data"] = raw_data_from_file['regions_data']
            economic_summary["regions_summary"] = raw_data_from_file['regions_summary']
            print(f"Załadowano dane o {len(raw_data_from_file['regions_data'])} regionach z bonusami")

        progress.add_tasks(1)
        wars_summary = build_wars_summary(raw_data_from_file, country_map)
        progress.advance(note="Podsumowanie wojen")
        print(f"Przetworzono podsumowanie wojen: {len(wars_summary.get('active_wars', []))} aktywnych wojen")
        fetched_at_for_report = raw_data_from_file.get('fetched_at')
        current_summary: Dict[str, Any] = {
            "military_summary": military_summary,
            "economic_summary": economic_summary,
            "wars_summary": wars_summary,
            "fetched_at": fetched_at_for_report,
            "top_warriors": top_warriors,
        }

        # Generuj tabele produktywności
        if raw_data_from_file.get('regions_data') and raw_data_from_file.get('eco_countries'):
            try:
                from production_analyzer_consolidated import ProductionAnalyzer
                analyzer = ProductionAnalyzer()
                production_data = analyzer.analyze_all_regions(raw_data_from_file['regions_data'])
                current_summary["production_data"] = production_data
                print(f"Generated productivity data for {len(production_data)} regions")
            except Exception as e:
                print(f"Błąd podczas generowania danych produktywności: {e}")
                current_summary["production_data"] = []

        progress.add_tasks(1)
        report_file = generate_report(
            current_summary,
            historical_data,
            top_warriors,
            items_map,
            currencies_map,
            country_map,
            currency_codes_map,
            gold_id_cache,
            "reports",
            sections,
        )
        progress.advance(note="Generowanie raportu DOCX")
        print(f"Raport DOCX wygenerowany: {report_file}")
        
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
        print(f"\n✅ Raport DOCX został pomyślnie wygenerowany: {report_file}")
        print(f"📊 Dane historyczne zapisane dla: {today_key}")
        progress.finish(final_note="Zakończono")
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania danych: {e}")
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
        print("🗄️ Baza danych zainicjalizowana")
    except Exception as e:
        print(f"⚠️ Uwaga: inicjalizacja bazy danych nie powiodła się: {e}")

    progress = ConsoleProgress()
    print("🚀 Start procesu: pobieranie danych i generowanie raportu HTML...")
    print("⚡ Zawsze pobieram świeże dane z API (cache wyłączony)")

    # Zawsze pobieraj świeże dane z API - cache wyłączony
    print("Pobieram świeże dane z API...")
    raw_data_dump: Dict[str, Any] = {}
    try:
        # Pobranie listy wojen
        progress.add_tasks(1)
        raw_data_dump['wars'] = fetch_data("wars", "wojnach")
        try:
            if raw_data_dump['wars']:
                save_snapshot("wars", raw_data_dump['wars'])
        except Exception:
            pass
        progress.advance(note="Lista wojen")
        
        # Sprawdź czy mamy dane o wojnach w cache
        if not raw_data_dump['wars'] or not raw_data_dump['wars'].get('data'):
            print("Brak danych o wojnach - pomijam pobieranie rund i uderzeń")
            raw_data_dump['hits'] = {}
            progress.advance(note="Brak wojen - pominięto")
            return

        # Równoległe pobieranie rund i uderzeń (ograniczona liczba wątków)
        hits_result: Dict[str, Any] = {}
        if raw_data_dump['wars'] and raw_data_dump['wars'].get('data'):
                yesterday = datetime.now() - timedelta(days=1)
                war_ids: List[int] = [w.get('id') for w in raw_data_dump['wars']['data'] if w.get('id') is not None]

                # Ogranicz liczbę wojen do analizy dla lepszej wydajności
                max_wars_to_analyze = int(os.getenv("MAX_WARS_TO_ANALYZE", "20"))
                if len(war_ids) > max_wars_to_analyze:
                    print(f"Ograniczam analizę do {max_wars_to_analyze} wojen z {len(war_ids)} dostępnych")
                    war_ids = war_ids[:max_wars_to_analyze]

                max_workers = int(os.getenv("API_WORKERS_WAR", "12"))

                # Etap 1: pobierz rundy dla wszystkich wojen równolegle
                def fetch_rounds(war_id: int) -> Tuple[int, List[Dict[str, Any]]]:
                    rounds_payload = fetch_data(f"war/rounds?war_id={war_id}", f"rundach wojny {war_id}")
                    rounds = (rounds_payload or {}).get('data') or []
                    try:
                        if rounds_payload:
                            save_snapshot("war/rounds", {"war_id": war_id, "data": rounds_payload})
                    except Exception:
                        pass
                    return war_id, rounds

                rounds_per_war: Dict[int, List[Dict[str, Any]]] = {}
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(fetch_rounds, wid): wid for wid in war_ids}
                    progress.add_tasks(len(futures))
                    for fut in as_completed(futures):
                        try:
                            wid, rounds = fut.result()
                            rounds_per_war[wid] = rounds
                            progress.advance(note=f"Rundy wojny {wid}")
                        except Exception:
                            progress.advance(note="Błąd rundy")

                # Etap 2: z rund po wczoraj pobierz uderzenia równolegle
                def should_fetch_round(r: Dict[str, Any]) -> bool:
                    end_date_str = r.get('end_date')
                    if not end_date_str:
                        return False
                    try:
                        end_date = datetime.fromisoformat(str(end_date_str).replace('Z', '+00:00'))
                    except Exception:
                        return False
                    # Ogranicz do rund z ostatnich 24h dla lepszej wydajności
                    return end_date > yesterday and end_date > (datetime.now() - timedelta(hours=24))

                round_ids_to_fetch: List[int] = []
                for rounds in rounds_per_war.values():
                    for r in rounds:
                        if should_fetch_round(r):
                            rid = r.get('id')
                            if isinstance(rid, int):
                                round_ids_to_fetch.append(rid)

                def fetch_hits(round_id: int) -> Tuple[int, Any]:
                    payload = fetch_data(f"war/round/hits?war_round_id={round_id}", f"uderzeniach rundy {round_id}")
                    try:
                        if payload:
                            save_snapshot("war/round/hits", {"round_id": round_id, "data": payload})
                    except Exception:
                        pass
                    return round_id, payload

                if round_ids_to_fetch:
                    max_workers_hits = int(os.getenv("API_WORKERS_HITS", "16"))
                    with ThreadPoolExecutor(max_workers=max_workers_hits) as executor:
                        futures = {executor.submit(fetch_hits, rid): rid for rid in round_ids_to_fetch}
                        progress.add_tasks(len(futures))
                        for fut in as_completed(futures):
                            try:
                                rid, payload = fut.result()
                                hits_result[str(rid)] = payload
                                progress.advance(note=f"Uderzenia runda {rid}")
                            except Exception:
                                progress.advance(note="Błąd uderzeń")

        if hits_result:
            raw_data_dump['hits'] = hits_result
            print(f"Pobrano dane o {len(hits_result)} rundach z uderzeniami")
        else:
            print("Brak danych o uderzeniach - używam pustego cache")
            raw_data_dump['hits'] = {}

        # Ekonomia
        progress.add_tasks(1)
        eco_countries, currencies_map, currency_codes_map, gold_id = fetch_countries_and_currencies()
        progress.advance(note="Kraje i waluty")
        
        # Sprawdź czy mamy dane ekonomiczne
        if not eco_countries or not currencies_map:
                print("Brak danych ekonomicznych - pomijam dalsze pobieranie")
                raw_data_dump['eco_countries'] = {}
                raw_data_dump['currencies_map'] = {}
                raw_data_dump['currency_codes_map'] = {}
                raw_data_dump['gold_id'] = GOLD_ID_FALLBACK
                return
                
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
        if eco_countries:
                # Usunięto pobieranie items_map - nie jest potrzebne do raportów
                # raw_data_dump['items_map'] = {}  # Pusty słownik zamiast pobierania
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
                else:
                    print("Używam cache kursów walut")
                # Usunięto obliczanie skrajności cen - nie jest potrzebne do raportów
                # raw_data_dump['cheapest_by_item'] = {}
                # raw_data_dump['expensive_by_item'] = {}
                
                # Pobierz najlepsze oferty pracy ze wszystkich krajów
                progress.add_tasks(1)
                raw_data_dump['best_jobs'] = fetch_best_jobs_from_all_countries(
                    eco_countries, raw_data_dump.get('currency_rates', {}), raw_data_dump['gold_id']
                )
                progress.advance(note="Ekonomia: najlepsze oferty pracy")
                
                # Pobierz najtańsze towary ze wszystkich krajów
                progress.add_tasks(1)
                # Pobierz mapę towarów jeśli nie ma w cache
                if not raw_data_dump.get('items_map'):
                    from economy import fetch_all_items
                    raw_data_dump['items_map'] = fetch_all_items()
                    print(f"DEBUG: Pobrano {len(raw_data_dump['items_map'])} towarów")
                else:
                    print(f"DEBUG: Używam cache z {len(raw_data_dump['items_map'])} towarami")
                
                # Użyj wszystkich krajów z eco_countries (już walidowanych podczas pobierania)
                valid_countries = eco_countries
                print(f"DEBUG: eco_countries count: {len(eco_countries) if eco_countries else 0}")
                
                if valid_countries:
                    print(f"Pobieranie najtańszych towarów dla {len(valid_countries)} krajów i {len(raw_data_dump.get('items_map', {}))} towarów...")
                    raw_data_dump['cheapest_items_all_countries'] = fetch_cheapest_items_from_all_countries(
                        valid_countries, raw_data_dump.get('items_map', {}), raw_data_dump.get('currency_rates', {}), raw_data_dump['gold_id']
                    )
                    print(f"Pobrano {len(raw_data_dump['cheapest_items_all_countries'])} najtańszych towarów")
                    progress.advance(note="Ekonomia: najtańsze towary ze wszystkich krajów")
                else:
                    print("Brak krajów do pobrania najtańszych towarów")
                    raw_data_dump['cheapest_items_all_countries'] = {}
                    progress.advance(note="Ekonomia: brak krajów")
                
                progress.add_tasks(1)
                raw_data_dump['currency_extremes'] = compute_currency_extremes(
                    raw_data_dump.get('currency_rates', {}), currencies_map, raw_data_dump['gold_id']
                )
                progress.advance(note="Ekonomia: kursy skrajne")
                
                # Pobierz dane o regionach z bonusami
                progress.add_tasks(1)
                regions_data, regions_summary = fetch_and_process_regions(eco_countries)
                if regions_data:
                    raw_data_dump['regions_data'] = regions_data
                    raw_data_dump['regions_summary'] = regions_summary
                    print(f"Pobrano dane o {len(regions_data)} regionach z bonusami")
                    try:
                        save_regions_data_to_storage(regions_data, regions_summary)
                    except Exception as e:
                        print(f"Błąd podczas zapisu danych o regionach do bazy: {e}")
                else:
                    print("Brak danych o regionach - używam pustego cache")
                    raw_data_dump['regions_data'] = []
                    raw_data_dump['regions_summary'] = {}
                progress.advance(note="Ekonomia: regiony z bonusami")

        raw_data_dump['fetched_at'] = datetime.now().isoformat()
        save_raw_api_output(raw_data_dump)
        raw_data_from_file = raw_data_dump
    except Exception as e:
        print(f"❌ Wystąpił błąd przy pobieraniu danych: {e}")
        import traceback
        traceback.print_exc()
        progress.finish(final_note="Przerwano z błędem")
        return
    # Użyj świeżo pobranych danych
    raw_data_from_file = raw_data_dump

    # Sprawdź czy dane zostały pomyślnie pobrane
    if not raw_data_dump:
        print("❌ Błąd: Nie można wczytać danych. Raport nie zostanie wygenerowany.")
        progress.finish(final_note="Brak danych")
        return

    # Uzupełnij brakujące dane ekonomiczne jeśli potrzeba
    try:
        eco_countries_cache = raw_data_from_file.get('eco_countries') or {}
        currencies_map_cache = raw_data_from_file.get('currencies_map') or {}
        currency_codes_map_cache = raw_data_from_file.get('currency_codes_map') or {}
        gold_id_cache = raw_data_from_file.get('gold_id') or GOLD_ID_FALLBACK
        items_map_cache = raw_data_from_file.get('items_map') or {}
        currency_rates_cache = raw_data_from_file.get('currency_rates') or {}

        # Jeśli wymuszono odświeżenie kursów/ekonomii, odśwież także mapy walut i GOLD ID
        if os.getenv("REFRESH_RATES", "0") == "1" or os.getenv("RECALC_ECONOMY", "0") == "1":
            try:
                eco_countries_cache, currencies_map_cache, currency_codes_map_cache, detected_gold_id = fetch_countries_and_currencies()
                if detected_gold_id is not None and detected_gold_id >= 0:
                    gold_id_cache = detected_gold_id
                # Zapisz odświeżone mapy w cache w pamięci
                raw_data_from_file['eco_countries'] = eco_countries_cache
                raw_data_from_file['currencies_map'] = currencies_map_cache
                raw_data_from_file['currency_codes_map'] = currency_codes_map_cache
                raw_data_from_file['gold_id'] = gold_id_cache
            except Exception:
                pass

        # Usunięto need_items_extremes - nie jest potrzebne do raportów
        need_items_extremes = False
        
        need_jobs_data = (
            bool(eco_countries_cache)
            and bool(currency_rates_cache)
            and not raw_data_from_file.get('best_jobs')
        )
        
        # Sprawdź czy potrzebne są dane o najtańszych towarach
        need_cheapest_items_all = (
            bool(eco_countries_cache)
            and bool(currency_rates_cache)
            and bool(items_map_cache)
            and not raw_data_from_file.get('cheapest_items_all_countries')
        )
        print(f"DEBUG: need_cheapest_items_all = {need_cheapest_items_all}")
        print(f"DEBUG: eco_countries_cache: {bool(eco_countries_cache)}, currency_rates_cache: {bool(currency_rates_cache)}, items_map_cache: {bool(items_map_cache)}, cheapest_items_exists: {bool(raw_data_from_file.get('cheapest_items_all_countries'))}")
        need_currency_extremes = (
            bool(currency_rates_cache)
            and bool(currencies_map_cache)
            and not raw_data_from_file.get('currency_extremes')
        )
        
        need_regions_data = (
            bool(eco_countries_cache)
            and (
                os.getenv("RECALC_ECONOMY", "0") == "1"
                or not raw_data_from_file.get('regions_data')
            )
        )

        # Jeżeli wymuszono odświeżenie kursów – przelicz kursy walut i skrajności niezależnie od powyższych flag
        if os.getenv("REFRESH_RATES", "0") == "1" and currencies_map_cache and (gold_id_cache is not None):
            try:
                currency_rates_cache = build_currency_rates_map(currencies_map_cache, gold_id_cache)
                raw_data_from_file['currency_rates'] = currency_rates_cache
                # Po zmianie kursów trzeba też odświeżyć skrajności
                need_currency_extremes = True
                # Usunięto need_items_extremes - nie jest potrzebne do raportów
                try:
                    save_snapshot("currency_rates", raw_data_from_file['currency_rates'])
                    save_currency_rates(raw_data_from_file['currency_rates'])
                except Exception:
                    pass
            except Exception:
                pass

        # Usunięto need_items_extremes - nie jest potrzebne do raportów
        # if need_items_extremes: ...
        
        if need_jobs_data:
            progress.add_tasks(1)
            raw_data_from_file['best_jobs'] = fetch_best_jobs_from_all_countries(
                eco_countries_cache, currency_rates_cache, gold_id_cache
            )
            progress.advance(note="Ekonomia (cache): oferty pracy uzupełnione")
        
        if need_cheapest_items_all:
            progress.add_tasks(1)
            # Pobierz mapę towarów jeśli nie ma w cache
            if not items_map_cache:
                from economy import fetch_all_items
                items_map_cache = fetch_all_items()
                raw_data_from_file['items_map'] = items_map_cache
            
            # Sprawdź czy kraje istnieją w API przed pobieraniem danych
            valid_countries_cache = {}
            for country_id, country_info in eco_countries_cache.items():
                try:
                    # Sprawdź czy kraj istnieje w API
                    test_url = f"country/{country_id}"
                    test_response = fetch_data(test_url, f"test kraju {country_id}")
                    if test_response is not None and test_response.get("code") == 200:
                        valid_countries_cache[country_id] = country_info
                    else:
                        print(f"Kraj {country_id} ({country_info.get('name', 'Unknown')}) nie istnieje w API - pomijam")
                except Exception as e:
                    print(f"Błąd podczas sprawdzania kraju {country_id}: {e}")
                    continue
            
            if valid_countries_cache:
                raw_data_from_file['cheapest_items_all_countries'] = fetch_cheapest_items_from_all_countries(
                    valid_countries_cache, items_map_cache, currency_rates_cache, gold_id_cache
                )
                progress.advance(note="Ekonomia (cache): najtańsze towary uzupełnione")
            else:
                print("Brak ważnych krajów do pobrania najtańszych towarów")
                raw_data_from_file['cheapest_items_all_countries'] = {}
                progress.advance(note="Ekonomia (cache): brak ważnych krajów")

        if need_currency_extremes:
            progress.add_tasks(1)
            raw_data_from_file['currency_extremes'] = compute_currency_extremes(
                currency_rates_cache, currencies_map_cache, gold_id_cache
            )
            progress.advance(note="Ekonomia (cache): kursy skrajne uzupełnione")
        
        if need_regions_data:
            progress.add_tasks(1)
            # Try to load from cache first
            regions_data, regions_summary = load_regions_data_from_storage()
            if not regions_data:
                # If no cached data, fetch fresh data
                print("Brak danych o regionach w cache - pobieranie świeżych danych...")
                regions_data, regions_summary = fetch_and_process_regions(eco_countries_cache)
                if regions_data:
                    try:
                        save_regions_data_to_storage(regions_data, regions_summary)
                    except Exception as e:
                        print(f"Błąd podczas zapisu danych o regionach do bazy (cache): {e}")
            
            if regions_data:
                raw_data_from_file['regions_data'] = regions_data
                raw_data_from_file['regions_summary'] = regions_summary
            progress.advance(note="Ekonomia (cache): regiony z bonusami uzupełnione")

        if need_currency_extremes or need_regions_data or need_cheapest_items_all:
            save_raw_api_output(raw_data_from_file)
            print("Zaktualizowano cache z nowymi danymi")
    except Exception as e:
        # Brakujące dane ekonomiczne w cache to nie-krytyczny błąd – kontynuujemy generowanie raportu
        print(f"⚠️ Uwaga: problem z cache ekonomicznym: {e}")
        pass

    historical_data = load_historical_data()
    today_key = datetime.now().strftime("%Y-%m-%d")

    try:
        # Bazuj na eco_countries aby uniknąć dodatkowego requestu /countries
        country_map = {}
        eco_countries: Dict[int, Dict[str, Any]] = raw_data_from_file.get('eco_countries', {})
        if eco_countries:
            country_map = {cid: cinfo.get('name') for cid, cinfo in eco_countries.items() if cinfo.get('name')}
        else:
            # Fallback: spróbuj pobrać listę krajów z /countries
            try:
                countries_payload = fetch_data("countries", "krajach")
                if countries_payload and countries_payload.get('data'):
                    country_map = {row.get('id'): row.get('name') for row in countries_payload['data'] if row.get('id') is not None}
            except Exception:
                pass

        # Przetwarzanie danych wojskowych
        progress.add_tasks(1)
        military_summary, top_warriors = process_hits_data(raw_data_from_file, country_map)
        progress.advance(note="Przetwarzanie uderzeń")
        print(f"Przetworzono dane wojskowe: {len(military_summary.get('damage_by_country', {}))} krajów")

        # items_map jest potrzebne do mapowania nazw towarów w sekcji "Najtańsze towary"
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
        # Usunięto cheapest_by_item i expensive_by_item - nie są potrzebne do raportów
        # economic_summary["cheapest_by_item"] = {}
        # economic_summary["most_expensive_by_item"] = {}
        # Include currency rates for rendering a sorted rates table in the report
        if raw_data_from_file.get('currency_rates'):
            economic_summary["currency_rates"] = raw_data_from_file['currency_rates']
        
        # Dodaj dane o ofertach pracy
        if raw_data_from_file.get('best_jobs'):
            economic_summary["best_jobs"] = raw_data_from_file['best_jobs']
            print(f"Załadowano {len(raw_data_from_file['best_jobs'])} najlepszych ofert pracy")
        
        # Dodaj dane o najtańszych towarach ze wszystkich krajów
        if raw_data_from_file.get('cheapest_items_all_countries'):
            economic_summary["cheapest_items_all_countries"] = raw_data_from_file['cheapest_items_all_countries']
            print(f"Loaded {len(raw_data_from_file['cheapest_items_all_countries'])} cheapest items from all countries")
            
        # Dodaj dane o najniższych NPC wage
        if raw_data_from_file.get('currency_rates') and raw_data_from_file.get('eco_countries'):
            try:
                lowest_npc_wage = get_lowest_npc_wage_countries(
                    raw_data_from_file['currency_rates'], 
                    raw_data_from_file['eco_countries']
                )
                economic_summary["lowest_npc_wage"] = lowest_npc_wage
                print(f"Loaded NPC wages data for {len(lowest_npc_wage)} countries")
            except Exception as e:
                print(f"Błąd podczas pobierania danych o najniższych NPC wage: {e}")
        
        # Dodaj dane o regionach z bonusami
        if raw_data_from_file.get('regions_data'):
            economic_summary["regions_data"] = raw_data_from_file['regions_data']
            economic_summary["regions_summary"] = raw_data_from_file['regions_summary']
            print(f"Załadowano dane o {len(raw_data_from_file['regions_data'])} regionach z bonusami")

        progress.add_tasks(1)
        wars_summary = build_wars_summary(raw_data_from_file, country_map)
        progress.advance(note="Podsumowanie wojen")
        print(f"Przetworzono podsumowanie wojen: {len(wars_summary.get('active_wars', []))} aktywnych wojen")
        fetched_at_for_report = raw_data_from_file.get('fetched_at')
        current_summary: Dict[str, Any] = {
            "military_summary": military_summary,
            "economic_summary": economic_summary,
            "wars_summary": wars_summary,
            "fetched_at": fetched_at_for_report,
            "top_warriors": top_warriors,
        }

        # Generuj tabele produktywności
        if raw_data_from_file.get('regions_data') and raw_data_from_file.get('eco_countries'):
            try:
                from production_analyzer_consolidated import ProductionAnalyzer
                analyzer = ProductionAnalyzer()
                production_data = analyzer.analyze_all_regions(raw_data_from_file['regions_data'])
                current_summary["production_data"] = production_data
                print(f"Generated productivity data for {len(production_data)} regions")
            except Exception as e:
                print(f"Błąd podczas generowania danych produktywności: {e}")
                current_summary["production_data"] = []

        progress.add_tasks(1)
        report_file = generate_html_report(
            current_summary,
            historical_data,
            top_warriors,
            items_map,
            currencies_map,
            country_map,
            currency_codes_map,
            gold_id_cache,
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
        print(f"\n✅ Raport HTML został pomyślnie wygenerowany: {report_file}")
        print(f"📊 Dane historyczne zapisane dla: {today_key}")
        progress.finish(final_note="Zakończono")
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania danych: {e}")
        import traceback
        traceback.print_exc()
        progress.finish(final_note="Przerwano z błędem")
        return


if __name__ == "__main__":
    run_html()


