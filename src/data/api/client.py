import json
import os
import requests
from typing import Any, Dict, Optional
from config.settings.base import AUTH_TOKEN, ECLESIAR_API_KEY, API_BASE_URL

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _with_api_key(url: str) -> str:
    if not ECLESIAR_API_KEY:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}api_key={ECLESIAR_API_KEY}"


def _load_cookies() -> Dict[str, str]:
    """Load cookies from eclesiar_cookies.json as fallback for authentication"""
    try:
        cookies_file = "data/eclesiar_cookies.json"
        if os.path.exists(cookies_file):
            with open(cookies_file, 'r') as f:
                cookies_data = json.load(f)
                return cookies_data
    except Exception as e:
        print(f"Warning: Could not load cookies: {e}")
    return {}


def _headers() -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    # Try AUTH_TOKEN first
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    else:
        # Fallback to cookies
        cookies = _load_cookies()
        if cookies:
            # Convert cookies to Cookie header format
            cookie_string = "; ".join([f"{key}={value}" for key, value in cookies.items()])
            headers["Cookie"] = cookie_string
            print("Using cookies for authentication (AUTH_TOKEN not available)")
        else:
            print("Warning: No AUTH_TOKEN and no cookies available for authentication")
    
    return headers


# Globalna sesja HTTP z retry i keep-alive
_SESSION: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is not None:
        return _SESSION

    session = requests.Session()
    retries_total = int(os.getenv("API_RETRIES", "3"))
    backoff = float(os.getenv("API_BACKOFF", "0.5"))
    retry = Retry(
        total=retries_total,
        connect=retries_total,
        read=retries_total,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=50)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _SESSION = session
    return session


def fetch_data(endpoint: str, description: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    api_url = f"{API_BASE_URL}/{endpoint}"
    api_url = _with_api_key(api_url)
    verbose = os.getenv("API_VERBOSE", "1") == "1"
    if verbose:
        print(f"Fetching data: {description} from URL: {api_url}...")
    try:
        timeout_sec = float(os.getenv("API_TIMEOUT", "10"))
        response = _get_session().get(api_url, headers=_headers(), params=params, timeout=timeout_sec)
        
        # Sprawdź status code i obsłuż błędy odpowiednio
        if response.status_code == 404:
            print(f"Endpoint {endpoint} nie istnieje (404) - {description}")
            return None
        elif response.status_code >= 400:
            print(f"HTTP error {response.status_code} for {endpoint}: {description}")
            response.raise_for_status()
        
        data = response.json()
        if verbose:
            # Ogranicz bardzo duże logi
            try:
                preview = json.dumps(data, indent=2)
                if len(preview) > 3000:
                    preview = preview[:3000] + "... (truncated)"
                print(f"--- Data about {description} ---\n{preview}\n")
            except Exception:
                pass
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {description}: {e}")
        return None


