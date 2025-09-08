# Aktualizacja Skróconego Raportu Ekonomicznego

## Zmiany w skróconym raporcie

### **Przed aktualizacją:**
- Raport pokazywał tylko **najlepszy region** dla każdego produktu
- Tytuł: "Best Regions for Production"
- Jedna tabela na produkt z najlepszym regionem

### **Po aktualizacji:**
- Raport pokazuje **po jednym przykładzie z każdego produktu i każdej jakości (Q1-Q5)**
- Tytuł: "Production Examples by Product and Quality"
- Jedna tabela na produkt z wszystkimi jakościami Q1-Q5

## Struktura raportu

### **Sekcja 3: Production Examples by Product and Quality**

Dla każdego produktu pokazuje:
- **Region** - najlepszy region dla tego produktu
- **Country** - kraj regionu
- **Score** - score efektywności
- **Bonus** - bonus regionalny
- **Q1-Q5** - produkcja dla każdej jakości

### **Przykład tabeli:**

| Region | Country | Score | Bonus | Q1 | Q2 | Q3 | Q4 | Q5 |
|--------|---------|-------|-------|----|----|----|----|----|
| Sample Region 2 | Sample Country | 64.47 | 20.0% | 213 | 155 | 113 | 83 | 60 |

## Produkty w raporcie

1. **Weapon** - broń lądowa
2. **Grain** - zboże (surowiec)
3. **Iron** - żelazo (surowiec)
4. **Titanium** - tytan (surowiec)
5. **Fuel** - paliwo (surowiec)
6. **Aircraft** - broń lotnicza
7. **Food** - jedzenie
8. **Airplane Ticket** - bilety lotnicze

## Korzyści

- **Kompletny przegląd** wszystkich produktów i jakości
- **Łatwe porównanie** produkcji Q1-Q5
- **Najlepsze regiony** dla każdego produktu
- **Zwięzły format** - jeden wiersz na produkt

## Użycie

```bash
python3 main.py short-economic-report
```

Raport zostanie zapisany w katalogu `reports/` jako plik DOCX.

