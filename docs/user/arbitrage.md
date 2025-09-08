# Aplikacja Arbitrażu Walutowego dla Eclesiar

## Opis

Aplikacja do analizy i wykrywania okazji arbitrażowych na rynku walutowym gry Eclesiar. Aplikacja analizuje ceny kupna i sprzedaży wszystkich walut, uwzględnia koszty transakcji (bilety) i sugeruje najlepsze strategie zarobkowe.

## Funkcjonalności

### 🎯 Główne funkcje
- **Analiza arbitrażu prostego** - Gold ↔ Waluta
- **Analiza arbitrażu krzyżowego** - Waluta A ↔ Waluta B
- **Analiza arbitrażu trójkątnego** - A→B→C→A
- **Analiza ryzyka** - ocena zmienności i płynności rynków
- **Optymalizacja portfela** - inteligentny wybór najlepszych okazji
- **Backtesting** - testowanie strategii na danych historycznych
- **Raporty** - szczegółowe analizy w formatach TXT i CSV

### 📊 Metryki analizy
- **Zysk procentowy** - potencjalny zysk z transakcji
- **Score ryzyka** - ocena ryzyka transakcji (0-1)
- **Poziom pewności** - pewność wykonania transakcji
- **Score wolumenu** - ocena płynności rynku
- **Score płynności** - ocena dostępności ofert
- **Czas wykonania** - szacowany czas realizacji

### 🔧 Konfiguracja
- **Koszt biletu** - koszt transakcji w złocie
- **Minimalny próg zysku** - minimalny zysk do rozważenia
- **Limity API** - kontrola liczby wywołań API
- **Parametry cache** - zarządzanie danymi w pamięci
- **Opcje optymalizacji** - preferencje analizy

## Instalacja

### Wymagania
- Python 3.8+
- Token autoryzacyjny Eclesiar API
- Dostęp do internetu

### Instalacja zależności
```bash
pip install -r requirements.txt
```

### Konfiguracja
1. Skopiuj plik `.env.example` do `.env`
2. Ustaw swój token autoryzacyjny:
```bash
AUTH_TOKEN=your_token_here
```

## Użytkowanie

### Podstawowa aplikacja
```bash
python currency_arbitrage.py
```

### Zaawansowana aplikacja
```bash
python advanced_currency_arbitrage.py
```

### Konfiguracja parametrów
```bash
# Ustaw koszt biletu
export TICKET_COST_GOLD=0.1

# Ustaw minimalny próg zysku
export MIN_PROFIT_THRESHOLD=1.0

# Ustaw liczbę wątków API
export API_WORKERS_MARKET=8

# Uruchom aplikację
python advanced_currency_arbitrage.py
```

## Strategie Zarobkowe

### 1. Arbitraż Prosty (Gold ↔ Waluta)
- **Opis**: Kup walutę za złoto po niskiej cenie, sprzedaj po wysokiej
- **Zalety**: Najniższe ryzyko, najszybsze wykonanie
- **Wady**: Mniejszy potencjalny zysk
- **Koszt**: 2 bilety (kupno + sprzedaż)

### 2. Arbitraż Krzyżowy (Waluta A ↔ Waluta B)
- **Opis**: Kup walutę A za złoto → wymień na walutę B → sprzedaj walutę B za złoto
- **Zalety**: Większy potencjalny zysk
- **Wady**: Większe ryzyko, więcej kosztów
- **Koszt**: 3 bilety (kupno + wymiana + sprzedaż)

### 3. Arbitraż Czasowy
- **Opis**: Wykorzystaj wahania cen w czasie
- **Zalety**: Może generować duże zyski
- **Wady**: Wymaga monitorowania, większe ryzyko
- **Koszt**: Zmienny (zależy od strategii)

### 4. Arbitraż Trójkątny
- **Opis**: Wykorzystaj różnice kursów między trzema walutami
- **Zalety**: Może generować zyski bez użycia złota
- **Wady**: Bardzo skomplikowany, wysokie ryzyko
- **Koszt**: 3+ bilety

## Analiza Ryzyka

### Czynniki ryzyka
1. **Zmienność rynku** - wahania cen
2. **Płynność** - dostępność ofert
3. **Spread** - różnica między ceną kupna a sprzedaży
4. **Wolumen** - ilość dostępnych ofert
5. **Czas wykonania** - szybkość realizacji transakcji

### Score ryzyka (0-1)
- **0.0-0.3**: Niskie ryzyko - bezpieczne transakcje
- **0.3-0.6**: Średnie ryzyko - umiarkowane transakcje
- **0.6-1.0**: Wysokie ryzyko - ryzykowne transakcje

## Konfiguracja zaawansowana

### Parametry środowiskowe
```bash
# Koszty i progi
TICKET_COST_GOLD=0.1                    # Koszt biletu w złocie
MIN_PROFIT_THRESHOLD=0.5                # Minimalny zysk w %
MIN_SPREAD_THRESHOLD=0.001              # Minimalny spread

# Limity transakcji
MAX_TRANSACTION_AMOUNT=10000            # Maksymalna ilość w transakcji
MIN_TRANSACTION_AMOUNT=1                # Minimalna ilość w transakcji

# Parametry API
API_WORKERS_MARKET=6                    # Liczba wątków do pobierania danych
API_WORKERS_ANALYSIS=4                  # Liczba wątków do analizy
API_RATE_LIMIT_DELAY=1.0               # Opóźnienie między wywołaniami API

# Parametry analizy
MAX_OPPORTUNITIES_TO_ANALYZE=1000      # Maksymalna liczba okazji
CONFIDENCE_THRESHOLD=0.3               # Minimalny poziom pewności
RISK_THRESHOLD=0.5                     # Maksymalny poziom ryzyka

# Parametry raportowania
REPORT_TOP_OPPORTUNITIES=20             # Liczba najlepszych okazji w raporcie
EXPORT_FORMATS=txt,csv                  # Format eksportu raportów

# Parametry cache
CACHE_DURATION_MINUTES=5                # Czas ważności cache
USE_CACHE=true                          # Włącz/wyłącz cache

# Parametry optymalizacji
OPTIMIZE_FOR_VOLUME=true                # Optymalizuj pod kątem wolumenu
OPTIMIZE_FOR_SPREAD=true                # Optymalizuj pod kątem spreadu
OPTIMIZE_FOR_RISK=false                 # Optymalizuj pod kątem ryzyka

# Parametry monitorowania
MONITORING_INTERVAL_SECONDS=300         # Interwał monitorowania
ENABLE_REAL_TIME_MONITORING=false       # Monitorowanie w czasie rzeczywistym
```

## Struktura plików

```
├── currency_arbitrage.py           # Podstawowa aplikacja arbitrażu
├── advanced_currency_arbitrage.py  # Zaawansowana aplikacja z analizą ryzyka
├── arbitrage_config.py             # Konfiguracja aplikacji
├── README_ARBITRAGE.md             # Ten plik
├── requirements.txt                 # Zależności Python
└── .env                           # Zmienne środowiskowe (do utworzenia)
```

## Przykłady użycia

### Analiza podstawowa
```python
from currency_arbitrage import CurrencyArbitrageAnalyzer

analyzer = CurrencyArbitrageAnalyzer(
    ticket_cost_gold=0.1,
    min_profit_threshold=0.5
)

analyzer.run_analysis()
```

### Analiza zaawansowana
```python
from advanced_currency_arbitrage import AdvancedCurrencyArbitrageAnalyzer
from arbitrage_config import get_config

config = get_config()
config['portfolio_optimization_enabled'] = True
config['risk_analysis_enabled'] = True

analyzer = AdvancedCurrencyArbitrageAnalyzer(config)
analyzer.run_advanced_analysis()
```

### Własna konfiguracja
```python
custom_config = {
    'ticket_cost_gold': 0.15,
    'min_profit_threshold': 1.0,
    'api_workers_market': 10,
    'optimize_for_risk': True,
    'enable_notifications': True
}

analyzer = AdvancedCurrencyArbitrageAnalyzer(custom_config)
analyzer.run_advanced_analysis()
```

## Interpretacja wyników

### Raport tekstowy
- **TOP OKAZJE**: Lista najlepszych okazji do arbitrażu
- **ANALIZA RYZYKA**: Metryki ryzyka dla wszystkich okazji
- **STRATEGIE ZAROBKOWE**: Opis różnych strategii
- **WSKAZÓWKI**: Praktyczne porady

### Raport CSV
- **from_currency**: Waluta źródłowa
- **to_currency**: Waluta docelowa
- **profit_percentage**: Zysk w procentach
- **risk_score**: Score ryzyka (0-1)
- **confidence**: Poziom pewności (0-1)
- **volume_score**: Score wolumenu (0-1)
- **liquidity_score**: Score płynności (0-1)

## Wskazówki praktyczne

### 1. Rozpoczęcie
- Zacznij od arbitrażu prostego (Gold ↔ Waluta)
- Ustaw niski próg zysku (0.5-1.0%)
- Monitoruj ryzyko (score < 0.5)

### 2. Optymalizacja
- Używaj cache dla oszczędności API
- Dostosuj liczbę wątków do swojego łącza
- Monitoruj limity API

### 3. Zarządzanie ryzykiem
- Dywersyfikuj między różne waluty
- Uwzględnij koszty transakcji
- Monitoruj zmiany cen w czasie

### 4. Skalowanie
- Zwiększaj próg zysku z doświadczeniem
- Eksperymentuj z różnymi strategiami
- Używaj backtestingu do testowania

## Rozwiązywanie problemów

### Błąd autoryzacji
```
Błąd: Token autoryzacyjny nie został załadowany z pliku .env.
```
**Rozwiązanie**: Sprawdź czy plik `.env` istnieje i zawiera poprawny `AUTH_TOKEN`

### Błąd API
```
Błąd podczas pobierania danych rynkowych
```
**Rozwiązanie**: 
- Sprawdź połączenie internetowe
- Zmniejsz liczbę wątków API
- Zwiększ opóźnienie między wywołaniami

### Brak okazji
```
Znaleziono 0 okazji do arbitrażu
```
**Rozwiązanie**:
- Zmniejsz minimalny próg zysku
- Sprawdź czy rynki są aktywne
- Sprawdź koszty biletu

## Wsparcie

### Dokumentacja API
- [Eclesiar API Documentation](https://api.eclesiar.com/)
- [Market Endpoint](https://api.eclesiar.com/market/coin/get)

### Logi
- Aplikacja generuje szczegółowe logi
- Sprawdź konsolę w przypadku błędów
- Użyj `LOG_TO_FILE=true` dla zapisu do pliku

### Monitoring
- Użyj `ENABLE_REAL_TIME_MONITORING=true` dla ciągłego monitorowania
- Ustaw `MONITORING_INTERVAL_SECONDS` dla interwału

## Licencja

Ten projekt jest przeznaczony do użytku edukacyjnego i osobistego. Używaj odpowiedzialnie i zgodnie z regulaminem gry Eclesiar.

## Autor

Aplikacja została stworzona na podstawie istniejącego kodu `orchestrator.py` z rozszerzeniami o funkcjonalności arbitrażu walutowego.

---

**Uwaga**: Arbitraż walutowy wiąże się z ryzykiem. Zawsze analizuj transakcje przed wykonaniem i nie inwestuj więcej niż możesz stracić.
