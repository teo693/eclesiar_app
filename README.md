# Eclesiar - Aplikacja do Analizy Danych Gry

Aplikacja do analizy danych z gry Eclesiar, generująca raporty dzienne, analizy produktywności regionów oraz analizy arbitrażu walutowego.

## 🏗️ Struktura Projektu

```
eclesiar/
├── main.py                           # Główny punkt wejścia
├── orchestrator.py                   # Główny orchestrator aplikacji
├── reporting.py                      # Generowanie raportów dziennych
├── production_analyzer_consolidated.py  # Analiza produktywności regionów
├── arbitrage_analyzer_consolidated.py   # Analiza arbitrażu walutowego
├── api_client.py                     # Klient API
├── economy.py                        # Funkcje ekonomiczne
├── military.py                       # Funkcje militarne
├── regions.py                        # Funkcje regionalne
├── storage.py                        # Zarządzanie danymi
├── db.py                            # Baza danych SQLite
├── config.py                         # Konfiguracja
├── arbitrage_config.py               # Konfiguracja arbitrażu
├── requirements.txt                  # Zależności Python
├── reports/                          # Raporty dzienne (DOCX, HTML)
├── production_analysis/              # Analizy produktywności
└── arbitrage_reports/                # Raporty arbitrażowe
```

## 🚀 Uruchomienie

### Instalacja zależności
```bash
pip install -r requirements.txt
```

### Uruchomienie aplikacji

#### 1. Generowanie dziennego raportu
```bash
python main.py daily-report
```

#### 2. Analiza produktywności regionów
```bash
python main.py production-analysis
```

#### 3. Analiza arbitrażu walutowego
```bash
python main.py arbitrage-analysis --min-profit 1.0
```

#### 4. Pełna analiza (wszystkie moduły)
```bash
python main.py full-analysis
```

### Opcje dodatkowe
```bash
python main.py daily-report --output-dir custom_reports
python main.py arbitrage-analysis --min-profit 2.0 --output-dir arbitrage_results
```

## 📊 Funkcjonalności

### 📋 Raporty Dziennie
- Statystyki militarne (wojny, uszkodzenia)
- Ranking najlepszych wojowników
- Analiza ekonomiczna (kursy walut, oferty pracy)
- Porównania z poprzednimi dniami
- Generowanie w formacie DOCX

### 🏭 Analiza Produktywności Regionów
- Obliczanie efektywności produkcji
- Uwzględnianie bonusów regionalnych i krajowych
- Analiza zanieczyszczeń i płac NPC
- Ranking regionów według score'u efektywności

### 💰 Analiza Arbitrażu Walutowego
- Wyszukiwanie okazji arbitrażowych
- Analiza ryzyka transakcji
- Ocena płynności rynków
- Generowanie raportów CSV i TXT
- Backtesting strategii

## ⚙️ Konfiguracja

### Plik .env
```env
API_KEY=your_api_key_here
API_URL=https://api.eclesiar.com
ECLESIAR_DB_PATH=eclesiar.db
```

### Konfiguracja arbitrażu (arbitrage_config.py)
```python
ARBITRAGE_CONFIG = {
    'min_profit_threshold': 0.5,  # Minimalny zysk w %
    'max_risk_score': 0.7,        # Maksymalny score ryzyka
    'ticket_cost_gold': 0.1,      # Koszt biletu w złocie
    'max_execution_time': 300     # Maksymalny czas wykonania w sekundach
}
```

## 📁 Organizacja Raportów

### Raporty dzienne
- **Lokalizacja**: `reports/`
- **Formaty**: DOCX, HTML
- **Nazewnictwo**: `raport_dzienny_YYYY-MM-DD_HH-MM.docx`

### Analizy produktywności
- **Lokalizacja**: `production_analysis/`
- **Formaty**: TXT
- **Nazewnictwo**: `production_analysis_YYYYMMDD_HHMMSS.txt`

### Raporty arbitrażowe
- **Lokalizacja**: `arbitrage_reports/`
- **Formaty**: CSV, TXT
- **Nazewnictwo**: `arbitrage_report_YYYYMMDD_HHMMSS.csv`

## 🔧 Rozwój

### Dodawanie nowych modułów
1. Utwórz nowy plik Python w głównym katalogu
2. Dodaj import w `main.py`
3. Dodaj nową komendę w parserze argumentów
4. Zaktualizuj dokumentację

### Testowanie
```bash
# Test pojedynczego modułu
python -c "from production_analyzer_consolidated import ProductionAnalyzer; print('OK')"

# Test pełnej aplikacji
python main.py full-analysis
```

## 📝 Historia Zmian

### v2.0 - Reorganizacja (2025-09-03)
- ✅ Usunięto duplikaty plików
- ✅ Skonsolidowano analizatory produkcji i arbitrażu
- ✅ Zorganizowano raporty w osobne foldery
- ✅ Utworzono główny punkt wejścia (`main.py`)
- ✅ Uporządkowano strukturę projektu
- ✅ Zaktualizowano dokumentację

### v1.0 - Wersja początkowa
- Podstawowe funkcjonalności raportowania
- Analiza produktywności regionów
- Analiza arbitrażu walutowego

## 🤝 Wsparcie

W przypadku problemów lub pytań:
1. Sprawdź logi aplikacji
2. Upewnij się, że wszystkie zależności są zainstalowane
3. Sprawdź konfigurację API w pliku `.env`
4. Sprawdź uprawnienia do zapisu w katalogach wyjściowych

## 📄 Licencja

Projekt prywatny - do użytku wewnętrznego.
