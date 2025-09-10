from collections import defaultdict
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings.base import GOLD_ID_FALLBACK
from src.data.api.client import fetch_data


def fetch_countries_and_currencies() -> Tuple[Dict[int, Dict[str, Any]], Dict[int, str], Dict[int, str], Optional[int]]:
    res = fetch_data("countries", "krajach i walutach")
    countries: Dict[int, Dict[str, Any]] = {}
    currencies: Dict[int, str] = {}
    currency_codes: Dict[int, str] = {}
    gold_id: Optional[int] = None

    if res and res.get("code") == 200 and isinstance(res.get("data"), list):
        for c in res["data"]:
            if not c.get("is_available", True):
                continue
            cid = c.get("id")
            name = c.get("name") or f"Country {cid}"
            cur = c.get("currency") or {}
            cur_id = cur.get("id")
            cur_name = cur.get("name") or f"Currency {cur_id}"
            cur_code = cur.get("code") or ""

            if cid is not None and cur_id is not None:
                countries[cid] = {
                    "name": name,
                    "currency_id": cur_id,
                    "currency_name": cur_name,
                    "currency_code": cur_code,
                }
                currencies[cur_id] = cur_name
                if cur_code:
                    currency_codes[cur_id] = cur_code
            # Identify GOLD as early as possible using reliable signals
            if gold_id is None:
                code_upper = (cur_code or "").strip().upper()
                name_lower = (cur_name or "").strip().lower()
                # Prefer currency code equality; fall back to name match
                if code_upper == "GOLD" or name_lower == "gold":
                    gold_id = cur_id

        # Final pass fallback: in case early detection missed (e.g., empty codes in some rows)
        if gold_id is None:
            for cur_id, cur_code in currency_codes.items():
                if (cur_code or "").strip().upper() == "GOLD":
                    gold_id = cur_id
                    break
        if gold_id is None:
            for cur_id, cur_name in currencies.items():
                if str(cur_name).strip().lower() == "gold":
                    gold_id = cur_id
                    break

    return countries, currencies, currency_codes, gold_id


def fetch_all_items() -> Dict[int, str]:
    items: Dict[int, str] = {}
    page = 1
    while True:
        url = f"server/items?page={page}"
        res = fetch_data(url, f"przedmiotach (strona {page})")
        if res and res.get("code") != 200:
            break
        data = res.get("data") or []
        if not data:
            break
        for it in data:
            iid = it.get("id")
            base_name = it.get("name") or f"Item {iid}"
            quality = it.get("quality") or it.get("q") or it.get("tier")
            # Normalize to lower-case for consistent display (e.g., "iron", "weapon q2")
            display_name = str(base_name).lower()
            try:
                q_int = int(quality) if quality is not None else None
            except Exception:
                q_int = None
            if q_int is not None and q_int > 0:
                if f"q{q_int}" not in display_name:
                    display_name = f"{display_name} q{q_int}"

            if iid is not None:
                items[iid] = display_name
        page += 1
    return items


def fetch_items_by_type(report_type: str = "daily") -> Dict[int, str]:
    """
    Fetch only the items needed for specific report types.
    This optimizes API calls by fetching only relevant items.
    """
    if report_type == "production":
        # For production analysis, only fetch items that can be produced
        production_items = {
            "grain": True,
            "iron": True, 
            "titanium": True,
            "fuel": True,
            "food": True,
            "weapon": True,
            "aircraft": True,
            "airplane ticket": True,
        }
        return _fetch_filtered_items(production_items)
    
    elif report_type == "economic":
        # For economic reports, fetch commonly traded items
        economic_items = {
            "grain": True,
            "iron": True,
            "titanium": True,
            "fuel": True,
            "food": True,
            "weapon": True,
            "aircraft": True,
            "airplane ticket": True,
            "coffee": True,
            "hammer": True,
            "focus": True,
            "protein bar": True,
        }
        return _fetch_filtered_items(economic_items)
    
    elif report_type == "arbitrage":
        # For arbitrage analysis, fetch commonly traded items
        arbitrage_items = {
            "grain": True,
            "iron": True,
            "titanium": True,
            "fuel": True,
            "food": True,
            "weapon": True,
            "aircraft": True,
            "airplane ticket": True,
            "coffee": True,
            "hammer": True,
            "focus": True,
            "protein bar": True,
        }
        return _fetch_filtered_items(arbitrage_items)
    
    else:
        # For daily reports or full analysis, fetch all items
        return fetch_all_items()


def _fetch_filtered_items(needed_items: Dict[str, bool]) -> Dict[int, str]:
    """
    Fetch only items that match the needed_items filter.
    """
    items: Dict[int, str] = {}
    page = 1
    while True:
        url = f"server/items?page={page}"
        res = fetch_data(url, f"przedmiotach (strona {page})")
        if res and res.get("code") != 200:
            break
        data = res.get("data") or []
        if not data:
            break
        for it in data:
            iid = it.get("id")
            base_name = it.get("name") or f"Item {iid}"
            quality = it.get("quality") or it.get("q") or it.get("tier")
            
            # Normalize to lower-case for consistent display
            display_name = str(base_name).lower()
            try:
                q_int = int(quality) if quality is not None else None
            except Exception:
                q_int = None
            if q_int is not None and q_int > 0:
                if f"q{q_int}" not in display_name:
                    display_name = f"{display_name} q{q_int}"
            
            # Check if this item is needed
            base_name_lower = str(base_name).lower()
            if base_name_lower in needed_items:
                items[iid] = display_name
                print(f"✅ Found needed item: {display_name}")
            else:
                print(f"⏭️ Skipping unnecessary item: {display_name}")
                
        page += 1
    return items


def fetch_currency_to_gold_rate(currency_id: int) -> Optional[float]:
    # Używamy transaction=SELL - oferty kupna waluty za GOLD
    url = f"market/coin/get?currency_id={currency_id}&transaction=SELL"
    res = fetch_data(url, f"currency rates {currency_id}")
    if res and res.get("code") == 200:
        offers = res.get("data") or []
        if offers:
            try:
                # Weź średnią z 3 najlepszych ofert
                rates = []
                for offer in offers[:3]:
                    rate = offer.get("rate")
                    if rate is not None:
                        try:
                            rates.append(float(rate))
                        except (ValueError, TypeError):
                            continue
                
                if rates:
                    return sum(rates) / len(rates)
            except Exception:
                pass
    return None


def build_currency_rates_map(currencies: Dict[int, str], gold_id: int) -> Dict[int, float]:
    """Buduje mapę kursów walut względem GOLD"""
    rates_map = {}
    
    # GOLD zawsze ma kurs 1.0
    if gold_id is not None:
        rates_map[gold_id] = 1.0
    
    # Pobierz kursy dla pozostałych walut
    for currency_id in currencies:
        if currency_id == gold_id:
            continue
        
        rate = fetch_currency_to_gold_rate(currency_id)
        if rate is not None and rate > 0:
            rates_map[currency_id] = rate
    
    return rates_map


def compute_currency_extremes(currency_rates: Dict[int, float], currencies: Dict[int, str], gold_id: int) -> Tuple[Tuple[int, float], Tuple[int, float]]:
    """Oblicza skrajne kursy walut (najdroższa i najtańsza)"""
    if not currency_rates:
        return (None, None)
    
    # Usuń GOLD z analizy
    rates_for_analysis = {cid: rate for cid, rate in currency_rates.items() if cid != gold_id}
    
    if not rates_for_analysis:
        return (None, None)
    
    # Znajdź najdroższą i najtańszą walutę
    most_expensive = max(rates_for_analysis.items(), key=lambda x: x[1])
    cheapest = min(rates_for_analysis.items(), key=lambda x: x[1])
    
    return most_expensive, cheapest


def fetch_best_jobs_from_all_countries(
    countries: Dict[int, Dict[str, Any]], 
    currency_rates: Dict[int, float], 
    gold_id: int
) -> List[Dict[str, Any]]:
    """Pobiera najlepsze oferty pracy ze wszystkich krajów"""
    best_jobs = []
    
    for country_id, country_info in countries.items():
        try:
            # Pobierz oferty pracy w danym kraju
            url = f"market/jobs/get?country_id={country_id}"
            res = fetch_data(url, f"ofertach pracy w kraju {country_info.get('name', country_id)}")
            
            if res and res.get("code") == 200:
                offers = res.get("data", [])
                if offers:
                    # Znajdź najlepszą ofertę w kraju
                    best_offer = None
                    best_salary_gold = 0
                    
                    for offer in offers:
                        salary = offer.get("salary")
                        if not salary:
                            continue
                            
                        try:
                            salary_f = float(salary)
                        except (ValueError, TypeError):
                            continue
                        
                        # Przelicz na GOLD
                        currency_id = country_info.get("currency_id")
                        if currency_id == gold_id:
                            salary_gold = salary_f
                        else:
                            rate = currency_rates.get(currency_id)
                            if not rate or rate <= 0:
                                continue
                            salary_gold = salary_f / rate
                        
                        if salary_gold > best_salary_gold:
                            best_salary_gold = salary_gold
                            best_offer = {
                                "country_name": country_info.get("name", f"Country {country_id}"),
                                "salary_original": salary_f,
                                "currency_name": country_info.get("currency_name", f"Currency {currency_id}"),
                                "salary_gold": salary_gold,
                                "job_title": offer.get("title", "Unknown Job")
                            }
                    
                    if best_offer:
                        best_jobs.append(best_offer)
                        
        except Exception as e:
            print(f"Error fetching job offers from country {country_id}: {e}")
            continue
    
    # Sortuj po wypłacie w gold (malejąco) i zwróć top 5
    best_jobs.sort(key=lambda x: x["salary_gold"], reverse=True)
    return best_jobs[:5]


def fetch_cheapest_items_from_all_countries(
    countries: Dict[int, Dict[str, Any]],
    items: Dict[int, str],
    currency_rates: Dict[int, float],
    gold_id: int
) -> Dict[int, List[Dict[str, Any]]]:
    """Pobiera najtańsze towary każdego rodzaju ze wszystkich krajów - zwraca listę 5 najtańszych dla każdego towaru"""
    cheapest_items = {}
    print(f"DEBUG: Starting to fetch cheapest goods for {len(items)} items from {len(countries)} countries")
    
    for item_id, item_name in items.items():
        all_items_for_type = []
        
        for country_id, country_info in countries.items():
            try:
                # Pobierz ceny towaru w danym kraju
                url = f"market/items/get?country_id={country_id}&item_id={item_id}"
                res = fetch_data(url, f"item price {item_name} in country{country_info.get('name', country_id)}")
                
                if res and res.get("code") == 200:
                    offers = res.get("data", [])
                    if offers:
                        # Parsuj oferty: (cena w walucie, ilość)
                        parsed = []
                        for offer in offers:
                            price = offer.get("value")
                            amount = offer.get("amount")
                            try:
                                price_f = float(price)
                            except Exception:
                                continue
                            try:
                                amount_i = int(amount) if amount is not None else 0
                            except Exception:
                                amount_i = 0
                            parsed.append((price_f, amount_i))

                        if not parsed:
                            continue

                        parsed.sort(key=lambda x: x[0])
                        min_price_currency = parsed[0][0]
                        amount_at_min = sum(a for p, a in parsed if p == min_price_currency)

                        # Kurs GOLD dla waluty kraju
                        currency_id = country_info.get("currency_id")
                        if currency_id == gold_id:
                            rate = 1.0
                        else:
                            rate = currency_rates.get(currency_id)
                        if not rate or rate <= 0:
                            continue

                        # Średnia z 5 najtańszych ofert w GOLD
                        top5 = parsed[:5]
                        avg5_gold = sum(p * rate for p, _ in top5) / len(top5)

                        # Minimalna cena w GOLD
                        min_price_gold = min_price_currency * rate

                        item_data = {
                            "item_id": item_id,
                            "item_name": item_name,
                            "country_id": country_id,
                            "country": country_info.get("name", f"Country {country_id}"),
                            "price_currency": min_price_currency,
                            "currency_id": currency_id,
                            "currency_name": country_info.get("currency_name", f"Currency {currency_id}"),
                            "price_gold": min_price_gold,
                            "amount": amount_at_min,
                            "avg5_in_gold": round(avg5_gold, 6),
                        }
                        all_items_for_type.append(item_data)
                                    
            except Exception as e:
                print(f"Error fetching prices for item {item_name} from country {country_id}: {e}")
                continue
        
        # Sortuj wszystkie towary tego typu według ceny w GOLD i weź 5 najtańszych
        if all_items_for_type:
            all_items_for_type.sort(key=lambda x: x["price_gold"])
            cheapest_items[item_id] = all_items_for_type[:5]
    
    print(f"DEBUG: Finished fetching cheapest goods. Found {len(cheapest_items)} item types")
    return cheapest_items


def fetch_currency_offers(
    currency_id: int, 
    transaction: Optional[str] = None, 
    page: int = 1
) -> List[Dict[str, Any]]:
    """Pobiera oferty walutowe"""
    url = f"market/coin/get?currency_id={currency_id}&page={page}"
    
    if transaction and transaction.upper() in ["BUY", "SELL"]:
        url += f"&transaction={transaction.upper()}"
    
    res = fetch_data(url, f"ofertach waluty {currency_id} (strona {page})")
    
    if res and res.get("code") == 200:
        offers = res.get("data") or []
        normalized_offers = []
        
        for offer in offers:
            rate = offer.get("rate")
            amount = offer.get("amount")
            owner = offer.get("owner", {})
            
            try:
                rate_f = float(rate) if rate is not None else None
                amount_i = int(amount) if amount is not None else None
            except (ValueError, TypeError):
                continue
            
            if rate_f is None or amount_i is None:
                continue
                
            normalized_offers.append({
                "rate": rate_f,
                "amount": amount_i,
                "owner": {
                    "id": owner.get("id"),
                    "type": owner.get("type", "account")
                }
            })
        
        return normalized_offers
    
    return []


def fetch_country_statistics(statistic: str) -> List[Dict[str, Any]]:
    """Pobiera statystyki krajów z API"""
    res = fetch_data(f"statistics/country?statistic={statistic}", f"country statistics ({statistic})")
    
    if not res or res.get("code") != 200:
        print(f"Error fetching statistics {statistic}")
        return []
    
    data = res.get("data", [])
    if not isinstance(data, list):
        return []
    
    countries = []
    for item in data:
        country = item.get("country", {})
        country_id = country.get("id")
        country_name = country.get("name", f"Country {country_id}")
        value = item.get("value", 0)
        
        countries.append({
            "id": country_id,
            "name": country_name,
            "value": value
        })
    
    return countries


def get_lowest_npc_wage_countries(currency_rates: Dict[int, float], countries_info: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Pobiera kraje z najniższymi NPC wage w przeliczeniu na gold"""
    npc_wage_data = fetch_country_statistics("npcwage")
    
    if not npc_wage_data:
        return []
    
    countries_with_gold_wage = []
    
    for country in npc_wage_data:
        country_id = country["id"]
        country_name = country["name"]
        npc_wage_local = country["value"]
        
        if npc_wage_local <= 0:
            continue
        
        country_info = countries_info.get(country_id)
        if not country_info:
            continue
            
        currency_id = country_info.get("currency_id")
        if not currency_id:
            continue
            
        currency_rate = currency_rates.get(currency_id, 0)
        if currency_rate <= 0:
            continue
            
        npc_wage_gold = npc_wage_local * currency_rate
        
        countries_with_gold_wage.append({
            "country_name": country_name,
            "npc_wage_local": npc_wage_local,
            "currency_name": country_info.get("currency_name", f"Currency {currency_id}"),
            "currency_code": country_info.get("currency_code", ""),
            "npc_wage_gold": npc_wage_gold
        })
    
    countries_with_gold_wage.sort(key=lambda x: x["npc_wage_gold"])
    return countries_with_gold_wage[:5]


