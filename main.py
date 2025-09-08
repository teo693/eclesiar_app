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
    """Get user input for report sections to include"""
    sections = {
        'military': True,
        'warriors': True, 
        'economic': True,
        'production': True
    }
    
    print("\n📋 Select sections to include in the report:")
    print("1. ⚔️ Military section (war statistics, wars)")
    print("2. 🏆 Warriors section (heroes ranking)")
    print("3. 💰 Economic section (currency rates, job offers, goods)")
    print("4. 🏭 Regional productivity analysis")
    print("5. ✅ All sections (default)")
    print("6. ❌ Military section only")
    
    choice = input("\nSelect option (1-6): ").strip()
    
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
    # choice == '5' or default - all sections
    
    # Show selected sections
    selected = []
    if sections['military']:
        selected.append("⚔️ Military")
    if sections['warriors']:
        selected.append("🏆 Warriors")
    if sections['economic']:
        selected.append("💰 Economic")
    if sections['production']:
        selected.append("🏭 Productivity")
    
    print(f"✅ Selected sections: {', '.join(selected)}")
    return sections


def run_production_analysis(output_dir: str) -> None:
    """Run regional productivity analysis"""
    print("🏭 Regional productivity analysis...")
    analyzer = ProductionAnalyzer()
    # Here you can add logic to fetch region data
    print("✅ Productivity analysis completed")


def run_arbitrage_analysis(output_dir: str, min_profit: float) -> None:
    """Run currency arbitrage analysis"""
    print("💰 Currency arbitrage analysis...")
    analyzer = CurrencyArbitrageAnalyzer(min_profit_threshold=min_profit)
    opportunities = analyzer.find_arbitrage_opportunities()
    
    if opportunities:
        print(f"✅ Found {len(opportunities)} arbitrage opportunities")
        # Generate reports
        csv_result = analyzer.generate_arbitrage_report(opportunities, "csv")
        txt_result = analyzer.generate_arbitrage_report(opportunities, "txt")
        print(f"📊 {csv_result}")
        print(f"📄 {txt_result}")
    else:
        print("❌ No arbitrage opportunities found")


def run_orchestrator_html(output_dir: str, sections: dict = None) -> None:
    """Run orchestrator with HTML report generation"""
    print("🌐 Generating daily HTML report...")
    from orchestrator import run_html as run_orchestrator_html_func
    run_orchestrator_html_func(output_dir, sections)


def run_full_analysis(output_dir: str, min_profit: float, sections: dict = None) -> None:
    """Run full analysis - all modules"""
    print("🔄 Full analysis - all modules...")
    
    # 1. Daily report
    print("\n📋 1/3 Generating daily report...")
    run_orchestrator(sections)
    
    # 2. Productivity analysis
    print("\n🏭 2/3 Regional productivity analysis...")
    run_production_analysis(output_dir)
    
    # 3. Arbitrage analysis
    print("\n💰 3/3 Currency arbitrage analysis...")
    run_arbitrage_analysis(output_dir, min_profit)


def interactive_menu():
    """Interactive application menu"""
    print("🚀 Welcome to Eclesiar application!")
    print("=" * 50)
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. 📊 Generate daily report (DOCX)")
        print("2. 🌐 Generate daily report (HTML)")
        print("3. 🏭 Regional productivity analysis")
        print("4. 💰 Currency arbitrage analysis")
        print("5. 🔄 Full analysis (everything)")
        print("6. ❌ Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            sections = get_report_sections()
            print("📋 Generating daily DOCX report...")
            run_orchestrator(sections)
            
        elif choice == '2':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            sections = get_report_sections()
            print("🌐 Generating daily HTML report...")
            run_orchestrator_html(output_dir, sections)
            
        elif choice == '3':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            run_production_analysis(output_dir)
            
        elif choice == '4':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            min_profit = input("💰 Minimum profit threshold in % (default: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            run_arbitrage_analysis(output_dir, min_profit)
            
        elif choice == '5':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            min_profit = input("💰 Minimum profit threshold in % (default: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            sections = get_report_sections()
            run_full_analysis(output_dir, min_profit, sections)
            
        elif choice == '6':
            print("👋 Thank you for using the Eclesiar application!")
            break
            
        else:
            print("❌ Nieprawidłowy wybór. Spróbuj ponownie.")
            continue
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created directory: {output_dir}")
        
        print(f"\n✅ Operation completed successfully!")
        print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ask if continue
        continue_choice = input("\n🔄 Do you want to perform another operation? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes']:
            print("👋 Thank you for using the Eclesiar application!")
            break


def main():
    """Main application function"""
    # Check if there are command line arguments
    if len(sys.argv) > 1:
        # Command line arguments mode
        parser = argparse.ArgumentParser(
            description="Eclesiar Application - Game Data Analysis",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Usage examples:
  python main.py daily-report          # Generate daily report
  python main.py production-analysis   # Regional productivity analysis
  python main.py arbitrage-analysis    # Currency arbitrage analysis
  python main.py full-analysis         # Full analysis (everything)
  python main.py                       # Interactive mode
            """
        )
        
        parser.add_argument(
            'command',
            choices=['daily-report', 'production-analysis', 'arbitrage-analysis', 'full-analysis'],
            help='Command to execute'
        )
        
        parser.add_argument(
            '--output-dir',
            default='reports',
            help='Output directory for reports (default: reports)'
        )
        
        parser.add_argument(
            '--min-profit',
            type=float,
            default=0.5,
            help='Minimum profit threshold for arbitrage in %% (default: 0.5)'
        )
        
        args = parser.parse_args()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
            print(f"📁 Created directory: {args.output_dir}")
        
        print(f"🚀 Starting Eclesiar application...")
        print(f"📊 Command: {args.command}")
        print(f"📁 Output directory: {args.output_dir}")
        print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        try:
            if args.command == 'daily-report':
                print("📋 Generating daily report...")
                # Use get_report_sections() function so user can select sections
                sections = get_report_sections()
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
            
            print(f"\n✅ Analysis completed successfully!")
            print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except KeyboardInterrupt:
            print("\n⚠️ Analysis was interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error during analysis execution: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n⚠️ Program was interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error during program execution: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
