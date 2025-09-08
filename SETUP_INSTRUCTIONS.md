# Instrukcje konfiguracji Eclesiar App

## 🔐 Konfiguracja API

### **1. Skopiuj plik konfiguracyjny:**
```bash
cp .env.example .env
```

### **2. Edytuj plik .env:**
```bash
nano .env
```

### **3. Uzupełnij klucz API:**
```bash
# Zamień YOUR_API_KEY_HERE na swój prawdziwy klucz API
AUTH_TOKEN="eclesiar_prod_TWOJ_PRAWDZIWY_KLUCZ_API"
```

### **4. Sprawdź konfigurację:**
```bash
# Test połączenia z API
curl -H "Authorization: Bearer eclesiar_prod_TWOJ_KLUCZ" https://api.eclesiar.com/countries
```

## 🚀 Uruchomienie aplikacji

### **Tryb interaktywny:**
```bash
python3 main.py
```

### **Tryb komend:**
```bash
# Skrócony raport ekonomiczny
python3 main.py short-economic-report

# Analiza produktywności regionów
python3 main.py production-analysis

# Analiza arbitrażu walutowego
python3 main.py arbitrage-analysis

# Pełna analiza
python3 main.py full-analysis
```

## 📁 Struktura plików

### **Pliki konfiguracyjne:**
- `.env.example` - przykładowa konfiguracja (bezpieczna do commitowania)
- `.env` - rzeczywista konfiguracja (ignorowana przez Git)

### **Pliki ignorowane przez Git:**
- `.env` - zawiera wrażliwe dane (klucze API)
- `*.db` - bazy danych
- `__pycache__/` - cache Pythona
- `reports/` - wygenerowane raporty
- `*.log` - pliki logów

## ⚠️ Bezpieczeństwo

### **Nigdy nie commituj:**
- Pliku `.env` z prawdziwymi kluczami API
- Plików z wrażliwymi danymi
- Kluczy autoryzacji

### **Zawsze commituj:**
- Plik `.env.example` (bez prawdziwych kluczy)
- Plik `.gitignore`
- Kod źródłowy

## 🔧 Rozwiązywanie problemów

### **Błąd 401 Unauthorized:**
1. Sprawdź czy klucz API jest kompletny
2. Sprawdź czy klucz nie wygasł
3. Sprawdź format: `eclesiar_prod_TWOJ_KLUCZ`

### **Brak dostępu do API:**
- Użyj przykładowego raportu do testowania
- Skontaktuj się z administracją Eclesiar

## 📊 Funkcje aplikacji

### **Skrócony raport ekonomiczny:**
- Kursy walut vs GOLD
- Najtańsze przedmioty
- Przykłady produkcji (Q1-Q5) dla każdego produktu

### **Analiza produktywności:**
- 8 czynników wpływających na produkcję
- Porównanie regionów
- Optymalizacja lokalizacji firm

### **Analiza arbitrażu:**
- Wykrywanie okazji arbitrażowych
- Analiza ryzyka
- Optymalizacja zysków

## 📞 Wsparcie

Jeśli masz problemy z konfiguracją:
1. Sprawdź plik `API_TROUBLESHOOTING.md`
2. Sprawdź logi aplikacji
3. Skontaktuj się z administracją Eclesiar
