#!/usr/bin/env python3
"""
Główny punkt wejścia do aplikacji Eclesiar.
Zapewnia czysty interfejs do wszystkich funkcjonalności.
"""

import os
import sys
import argparse
from datetime import datetime

from orchestrator import run as run_orchestrator
from production_analyzer_consolidated import ProductionAnalyzer
from arbitrage_analyzer_consolidated import CurrencyArbitrageAnalyzer


def get_report_sections() -> dict:
    """Pobiera od użytkownika informacje o sekcjach do zawarcia w raporcie"""
    sections = {
        'military': True,
        'warriors': True, 
        'economic': True,
        'production': True
    }
    
    print("\n📋 Wybierz sekcje do zawarcia w raporcie:")
    print("1. ⚔️ Sekcja militarna (statystyki wojenne, wojny)")
    print("2. 🏆 Sekcja wojowników (ranking bohaterów)")
    print("3. 💰 Sekcja ekonomiczna (kursy walut, oferty pracy, towary)")
    print("4. 🏭 Analiza produktywności regionów")
    print("5. ✅ Wszystkie sekcje (domyślnie)")
    print("6. ❌ Tylko sekcja militarna")
    
    choice = input("\nWybierz opcję (1-6): ").strip()
    
    if choice == '1':
        sections = {'military': True, 'warriors': False, 'economic': False, 'production': False}
    elif choice == '2':
        sections = {'military': False, 'warriors': True, 'economic': False, 'production': False}
    elif choice == '3':
        sections = {'military': False, 'warriors': False, 'economic': True, 'production': False}
    elif choice == '4':
        sections = {'military': False, 'warriors': False, 'economic': False, 'production': True}
    elif choice == '6':
        sections = {'military': True, 'warriors': False, 'economic': False, 'production': False}
    # choice == '5' lub domyślnie - wszystkie sekcje
    
    # Pokaż wybrane sekcje
    selected = []
    if sections['military']:
        selected.append("⚔️ Militarna")
    if sections['warriors']:
        selected.append("🏆 Wojownicy")
    if sections['economic']:
        selected.append("💰 Ekonomiczna")
    if sections['production']:
        selected.append("🏭 Produktywność")
    
    print(f"✅ Wybrane sekcje: {', '.join(selected)}")
    return sections


def run_production_analysis(output_dir: str) -> None:
    """Uruchamia analizę produktywności regionów"""
    print("🏭 Analiza produktywności regionów...")
    analyzer = ProductionAnalyzer()
    # Tutaj możesz dodać logikę do pobierania danych regionów
    print("✅ Analiza produktywności zakończona")


def run_arbitrage_analysis(output_dir: str, min_profit: float) -> None:
    """Uruchamia analizę arbitrażu walutowego"""
    print("💰 Analiza arbitrażu walutowego...")
    analyzer = CurrencyArbitrageAnalyzer(min_profit_threshold=min_profit)
    opportunities = analyzer.find_arbitrage_opportunities()
    
    if opportunities:
        print(f"✅ Znaleziono {len(opportunities)} okazji arbitrażowych")
        # Generuj raporty
        csv_result = analyzer.generate_arbitrage_report(opportunities, "csv")
        txt_result = analyzer.generate_arbitrage_report(opportunities, "txt")
        print(f"📊 {csv_result}")
        print(f"📄 {txt_result}")
    else:
        print("❌ Nie znaleziono okazji arbitrażowych")


def run_orchestrator_html(output_dir: str, sections: dict = None) -> None:
    """Uruchamia orchestrator z generowaniem raportu HTML"""
    print("🌐 Generowanie dziennego raportu HTML...")
    from orchestrator import run_html as run_orchestrator_html_func
    run_orchestrator_html_func(output_dir, sections)


def run_full_analysis(output_dir: str, min_profit: float, sections: dict = None) -> None:
    """Uruchamia pełną analizę - wszystkie moduły"""
    print("🔄 Pełna analiza - wszystkie moduły...")
    
    # 1. Dzienny raport
    print("\n📋 1/3 Generowanie dziennego raportu...")
    run_orchestrator(sections)
    
    # 2. Analiza produktywności
    print("\n🏭 2/3 Analiza produktywności regionów...")
    run_production_analysis(output_dir)
    
    # 3. Analiza arbitrażu
    print("\n💰 3/3 Analiza arbitrażu walutowego...")
    run_arbitrage_analysis(output_dir, min_profit)


def interactive_menu():
    """Interaktywne menu aplikacji"""
    print("🚀 Witaj w aplikacji Eclesiar!")
    print("=" * 50)
    
    while True:
        print("\n📋 Co chcesz zrobić?")
        print("1. 📊 Generuj dzienny raport (DOCX)")
        print("2. 🌐 Generuj dzienny raport (HTML)")
        print("3. 🏭 Analiza produktywności regionów")
        print("4. 💰 Analiza arbitrażu walutowego")
        print("5. 🔄 Pełna analiza (wszystko)")
        print("6. ❌ Wyjście")
        
        choice = input("\nWybierz opcję (1-6): ").strip()
        
        if choice == '1':
            output_dir = input("📁 Katalog wyjściowy (domyślnie: reports): ").strip() or 'reports'
            sections = get_report_sections()
            print("📋 Generowanie dziennego raportu DOCX...")
            run_orchestrator(sections)
            
        elif choice == '2':
            output_dir = input("📁 Katalog wyjściowy (domyślnie: reports): ").strip() or 'reports'
            sections = get_report_sections()
            print("🌐 Generowanie dziennego raportu HTML...")
            run_orchestrator_html(output_dir, sections)
            
        elif choice == '3':
            output_dir = input("📁 Katalog wyjściowy (domyślnie: reports): ").strip() or 'reports'
            run_production_analysis(output_dir)
            
        elif choice == '4':
            output_dir = input("📁 Katalog wyjściowy (domyślnie: reports): ").strip() or 'reports'
            min_profit = input("💰 Minimalny próg zysku w % (domyślnie: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            run_arbitrage_analysis(output_dir, min_profit)
            
        elif choice == '5':
            output_dir = input("📁 Katalog wyjściowy (domyślnie: reports): ").strip() or 'reports'
            min_profit = input("💰 Minimalny próg zysku w % (domyślnie: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            sections = get_report_sections()
            run_full_analysis(output_dir, min_profit, sections)
            
        elif choice == '6':
            print("👋 Dziękujemy za korzystanie z aplikacji Eclesiar!")
            break
            
        else:
            print("❌ Nieprawidłowy wybór. Spróbuj ponownie.")
            continue
        
        # Utwórz katalog wyjściowy jeśli nie istnieje
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Utworzono katalog: {output_dir}")
        
        print(f"\n✅ Operacja zakończona pomyślnie!")
        print(f"⏰ Czas zakończenia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Zapytaj czy kontynuować
        continue_choice = input("\n🔄 Czy chcesz wykonać kolejną operację? (t/n): ").strip().lower()
        if continue_choice not in ['t', 'tak', 'y', 'yes']:
            print("👋 Dziękujemy za korzystanie z aplikacji Eclesiar!")
            break


def main():
    """Główna funkcja aplikacji"""
    # Sprawdź czy są argumenty wiersza poleceń
    if len(sys.argv) > 1:
        # Tryb argumentów wiersza poleceń (stary sposób)
        parser = argparse.ArgumentParser(
            description="Aplikacja Eclesiar - analiza danych gry",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Przykłady użycia:
  python main.py daily-report          # Generuj dzienny raport
  python main.py production-analysis   # Analiza produktywności regionów
  python main.py arbitrage-analysis    # Analiza arbitrażu walutowego
  python main.py full-analysis         # Pełna analiza (wszystko)
  python main.py                       # Tryb interaktywny
            """
        )
        
        parser.add_argument(
            'command',
            choices=['daily-report', 'production-analysis', 'arbitrage-analysis', 'full-analysis'],
            help='Komenda do wykonania'
        )
        
        parser.add_argument(
            '--output-dir',
            default='reports',
            help='Katalog wyjściowy dla raportów (domyślnie: reports)'
        )
        
        parser.add_argument(
            '--min-profit',
            type=float,
            default=0.5,
            help='Minimalny próg zysku dla arbitrażu w %% (domyślnie: 0.5)'
        )
        
        args = parser.parse_args()
        
        # Utwórz katalog wyjściowy jeśli nie istnieje
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
            print(f"📁 Utworzono katalog: {args.output_dir}")
        
        print(f"🚀 Uruchamianie aplikacji Eclesiar...")
        print(f"📊 Komenda: {args.command}")
        print(f"📁 Katalog wyjściowy: {args.output_dir}")
        print(f"⏰ Czas rozpoczęcia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        try:
            if args.command == 'daily-report':
                print("📋 Generowanie dziennego raportu...")
                # Dla trybu wiersza poleceń, używamy wszystkich sekcji domyślnie
                sections = {
                    'military': True,
                    'warriors': True, 
                    'economic': True,
                    'production': True
                }
                run_orchestrator(sections)
                
            elif args.command == 'production-analysis':
                run_production_analysis(args.output_dir)
                    
            elif args.command == 'arbitrage-analysis':
                run_arbitrage_analysis(args.output_dir, args.min_profit)
                    
            elif args.command == 'full-analysis':
                # Dla trybu wiersza poleceń, używamy wszystkich sekcji domyślnie
                sections = {
                    'military': True,
                    'warriors': True, 
                    'economic': True,
                    'production': True
                }
                run_full_analysis(args.output_dir, args.min_profit, sections)
            
            print(f"\n✅ Analiza zakończona pomyślnie!")
            print(f"⏰ Czas zakończenia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except KeyboardInterrupt:
            print("\n⚠️ Analiza została przerwana przez użytkownika")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Błąd podczas wykonywania analizy: {e}")
            sys.exit(1)
    else:
        # Tryb interaktywny
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n⚠️ Program został przerwany przez użytkownika")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Błąd podczas wykonywania programu: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
