import json
import os
from typing import Any, Dict, List, Optional
from config import HISTORY_FILE, RAW_API_OUTPUT_FILE
from db import load_historical_reports, save_historical_report, load_raw_cache, save_raw_cache, save_regions_data


def load_historical_data() -> Dict[str, Any]:
    # Prefer DB storage; fallback to legacy file once for migration
    data = load_historical_reports()
    if data:
        return data
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
                if isinstance(legacy, dict):
                    fixed: Dict[str, Any] = {}
                    for key, value in legacy.items():
                        if key.startswith("20") and len(key) == 10:
                            fixed[key] = value
                            # opportunistic migrate
                            try:
                                save_historical_report(key, value)
                            except Exception:
                                pass
                    return fixed
                return legacy
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {}


def save_historical_data(data: Dict[str, Any]) -> None:
    # Store each date row into DB
    try:
        if isinstance(data, dict):
            for key, payload in data.items():
                if isinstance(payload, dict) and key and key.startswith("20") and len(key) == 10:
                    save_historical_report(key, payload)
        print("Dane historyczne zostały zapisane (DB).")
    except Exception as e:
        print(f"Błąd podczas zapisu historii do bazy: {e}")


def save_raw_api_output(data: Dict[str, Any]) -> None:
    try:
        save_raw_cache(data)
        print("Surowe dane z API zostały zapisane do bazy (cache).")
    except Exception as e:
        print(f"Błąd podczas zapisu surowych danych do bazy: {e}")


def load_raw_api_output() -> Optional[Dict[str, Any]]:
    # Prefer DB cache; fallback to legacy file for migration
    data = load_raw_cache()
    if data:
        return data
    if os.path.exists(RAW_API_OUTPUT_FILE):
        try:
            with open(RAW_API_OUTPUT_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
                try:
                    save_raw_cache(legacy)
                except Exception:
                    pass
                return legacy
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return None


def save_regions_data_to_storage(regions_data: List[Dict[str, Any]], regions_summary: Dict[str, Any]) -> None:
    """
    Zapisuje dane o regionach do storage (bazy danych).
    
    Args:
        regions_data: Lista regionów z bonusami
        regions_summary: Podsumowanie danych o regionach
    """
    try:
        save_regions_data(regions_data, regions_summary)
        print("Dane o regionach zostały zapisane do bazy danych.")
    except Exception as e:
        print(f"Błąd podczas zapisu danych o regionach: {e}")


