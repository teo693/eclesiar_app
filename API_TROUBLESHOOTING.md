# Rozwiązywanie problemów z API Eclesiar

## Problem: Błąd 401 Unauthorized

### **Objawy:**
```
Błąd HTTP 401 dla countries: krajach i walutach
Error fetching krajach i walutach: 401 Client Error: Unauthorized for url: https://api.eclesiar.com/countries
```

### **Przyczyna:**
Brak dostępu do API Eclesiar z powodu niepełnego lub nieprawidłowego klucza autoryzacji.

### **Obecna konfiguracja:**
```bash
# Plik .env
AUTH_TOKEN="eclesiar_prod_"
```

### **Rozwiązania:**

#### **1. Sprawdź klucz API:**
- Czy masz pełny klucz API z Eclesiar?
- Czy klucz nie wygasł?
- Czy klucz ma poprawny format: `eclesiar_prod_TWOJ_KLUCZ`

#### **2. Zaktualizuj plik .env:**
```bash
# Edytuj plik .env
nano .env

# Dodaj pełny klucz API
AUTH_TOKEN="eclesiar_prod_TWOJ_PELNY_KLUCZ_API"
```

#### **3. Sprawdź dostęp do API:**
```bash
# Test połączenia z API
curl -H "Authorization: Bearer eclesiar_prod_TWOJ_KLUCZ" https://api.eclesiar.com/countries
```

#### **4. Tymczasowe rozwiązanie:**
Jeśli nie masz dostępu do API, możesz użyć przykładowego raportu:
```bash
# Wygeneruj przykładowy raport
python3 test_short_report_offline.py
```

## **Co zostało zaktualizowane:**

### **Skrócony raport ekonomiczny:**
- ✅ **Po jednym przykładzie z każdego produktu i każdej jakości (Q1-Q5)**
- ✅ **Tytuł**: "Production Examples by Product and Quality"
- ✅ **Struktura**: Region, Country, Score, Bonus, Q1, Q2, Q3, Q4, Q5

### **Przykład danych:**
```
WEAPON:
  Region: Sample Region 2
  Score: 64.47
  Q1: 213, Q2: 155, Q3: 113, Q4: 83, Q5: 60
```

## **Następne kroki:**

1. **Uzyskaj pełny klucz API** z Eclesiar
2. **Zaktualizuj plik .env** z pełnym kluczem
3. **Przetestuj połączenie** z API
4. **Wygeneruj prawdziwy raport** z rzeczywistymi danymi

## **Kontakt:**
Jeśli potrzebujesz pomocy z kluczem API, skontaktuj się z administracją Eclesiar.
