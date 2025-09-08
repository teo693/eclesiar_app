import os
from dotenv import load_dotenv

# Upewnij się, że zmienne środowiskowe są załadowane
load_dotenv()

# Podstawowa konfiguracja aplikacji i API
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
ECLESIAR_API_KEY = os.getenv("ECLESIAR_API_KEY", "").strip()
API_BASE_URL = "https://api.eclesiar.com"

# Pliki używane do cache i historii
HISTORY_FILE = "data/historia_raportow.json"
RAW_API_OUTPUT_FILE = "data/raw_api_output.json"

# Domyślny GOLD ID, gdy nie wykryto z /countries
GOLD_ID_FALLBACK = -1

# Domyślna liczba workerów dla pobierania regionów
REGIONS_WORKERS_DEFAULT = 8

# ===== KONFIGURACJA ARBITRAŻU =====

# Koszty transakcji
TICKET_COST_GOLD = float(os.getenv("TICKET_COST_GOLD", "0.1"))

# Progi zysku
MIN_PROFIT_THRESHOLD = float(os.getenv("MIN_PROFIT_THRESHOLD", "0.5"))
MIN_SPREAD_THRESHOLD = float(os.getenv("MIN_SPREAD_THRESHOLD", "0.001"))

# Limity transakcji
MAX_TRANSACTION_AMOUNT = float(os.getenv("MAX_TRANSACTION_AMOUNT", "10000"))
MIN_TRANSACTION_AMOUNT = float(os.getenv("MIN_TRANSACTION_AMOUNT", "1"))

# Parametry API
API_WORKERS_MARKET = int(os.getenv("API_WORKERS_MARKET", "6"))
API_WORKERS_ANALYSIS = int(os.getenv("API_WORKERS_ANALYSIS", "4"))
API_WORKERS_REGIONS = int(os.getenv("API_WORKERS_REGIONS", "8"))
API_WORKERS_WAR = int(os.getenv("API_WORKERS_WAR", "12"))
API_WORKERS_HITS = int(os.getenv("API_WORKERS_HITS", "16"))

# Parametry analizy
MAX_OPPORTUNITIES_TO_ANALYZE = int(os.getenv("MAX_OPPORTUNITIES_TO_ANALYZE", "1000"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))
RISK_THRESHOLD = float(os.getenv("RISK_THRESHOLD", "0.5"))

# Parametry raportowania
REPORT_TOP_OPPORTUNITIES = int(os.getenv("REPORT_TOP_OPPORTUNITIES", "20"))
REPORT_INCLUDE_TRIANGULAR = bool(os.getenv("REPORT_INCLUDE_TRIANGULAR", "true").lower() == "true")

# Parametry cache
CACHE_DURATION_MINUTES = int(os.getenv("CACHE_DURATION_MINUTES", "5"))
USE_CACHE = bool(os.getenv("USE_CACHE", "true").lower() == "true")

# Parametry bezpieczeństwa
MAX_API_CALLS_PER_MINUTE = int(os.getenv("MAX_API_CALLS_PER_MINUTE", "60"))
API_RATE_LIMIT_DELAY = float(os.getenv("API_RATE_LIMIT_DELAY", "1.0"))

# Parametry eksportu
EXPORT_FORMATS = os.getenv("EXPORT_FORMATS", "txt,csv").split(",")
EXPORT_DIRECTORY = os.getenv("EXPORT_DIRECTORY", "reports")

# Parametry monitorowania
MONITORING_INTERVAL_SECONDS = int(os.getenv("MONITORING_INTERVAL_SECONDS", "300"))
ENABLE_REAL_TIME_MONITORING = bool(os.getenv("ENABLE_REAL_TIME_MONITORING", "false").lower() == "true")

# Parametry optymalizacji
OPTIMIZE_FOR_VOLUME = bool(os.getenv("OPTIMIZE_FOR_VOLUME", "true").lower() == "true")
OPTIMIZE_FOR_SPREAD = bool(os.getenv("OPTIMIZE_FOR_SPREAD", "true").lower() == "true")
OPTIMIZE_FOR_RISK = bool(os.getenv("OPTIMIZE_FOR_RISK", "false").lower() == "true")

# Parametry analizy historycznej
ENABLE_HISTORICAL_ANALYSIS = bool(os.getenv("ENABLE_HISTORICAL_ANALYSIS", "false").lower() == "true")
HISTORICAL_DATA_DAYS = int(os.getenv("HISTORICAL_DATA_DAYS", "7"))

# Parametry arbitrażu krzyżowego
CROSS_ARBITRAGE_ENABLED = bool(os.getenv("CROSS_ARBITRAGE_ENABLED", "true").lower() == "true")
CROSS_ARBITRAGE_MIN_PROFIT = float(os.getenv("CROSS_ARBITRAGE_MIN_PROFIT", "1.0"))

# Parametry arbitrażu czasowego
TEMPORAL_ARBITRAGE_ENABLED = bool(os.getenv("TEMPORAL_ARBITRAGE_ENABLED", "false").lower() == "true")
TEMPORAL_ARBITRAGE_WINDOW_HOURS = int(os.getenv("TEMPORAL_ARBITRAGE_WINDOW_HOURS", "24"))

# Parametry analizy ryzyka
RISK_ANALYSIS_ENABLED = bool(os.getenv("RISK_ANALYSIS_ENABLED", "true").lower() == "true")
MARKET_VOLATILITY_THRESHOLD = float(os.getenv("MARKET_VOLATILITY_THRESHOLD", "0.1"))
LIQUIDITY_THRESHOLD = float(os.getenv("LIQUIDITY_THRESHOLD", "1000"))

# Parametry backtestingu
BACKTESTING_ENABLED = bool(os.getenv("BACKTESTING_ENABLED", "false").lower() == "true")
BACKTESTING_PERIOD_DAYS = int(os.getenv("BACKTESTING_PERIOD_DAYS", "30"))
BACKTESTING_INITIAL_CAPITAL = float(os.getenv("BACKTESTING_INITIAL_CAPITAL", "1000"))

# Parametry eksperymentalne
EXPERIMENTAL_FEATURES_ENABLED = bool(os.getenv("EXPERIMENTAL_FEATURES_ENABLED", "false").lower() == "true")
MACHINE_LEARNING_ENABLED = bool(os.getenv("MACHINE_LEARNING_ENABLED", "false").lower() == "true")
PREDICTIVE_ANALYSIS_ENABLED = bool(os.getenv("PREDICTIVE_ANALYSIS_ENABLED", "false").lower() == "true")


