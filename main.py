#!/usr/bin/env python3
"""
Main entry point for the Eclesiar application.
Provides a clean interface to all functionalities.
"""

import os
import sys
import argparse
from datetime import datetime

from orchestrator import run as run_orchestrator
from production_analyzer_consolidated import ProductionAnalyzer
from arbitrage_analyzer_consolidated import CurrencyArbitrageAnalyzer
from short_economic_report import generate_short_economic_report
from production_calculator import ProductionCalculator


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
    try:
        # Use optimized orchestrator with production data only
        sections = {
            'military': False,
            'warriors': False, 
            'economic': False,
            'production': True
        }
        run_orchestrator(sections, "production")
        print("✅ Productivity analysis completed using optimized data fetching")
    except Exception as e:
        print(f"❌ Error during productivity analysis: {e}")


def run_arbitrage_analysis(output_dir: str, min_profit: float) -> None:
    """Run currency arbitrage analysis"""
    print("💰 Currency arbitrage analysis...")
    try:
        # Use optimized orchestrator with economic data only
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': False
        }
        run_orchestrator(sections, "arbitrage")
        print("✅ Arbitrage analysis completed using optimized data fetching")
    except Exception as e:
        print(f"❌ Error during arbitrage analysis: {e}")


def run_short_economic_report(output_dir: str) -> None:
    """Run short economic report generation"""
    print("📊 Generating short economic report...")
    try:
        report_path = generate_short_economic_report(output_dir)
        if report_path:
            print(f"✅ Short economic report generated: {report_path}")
        else:
            print("❌ Failed to generate short economic report")
    except Exception as e:
        print(f"❌ Error generating short economic report: {e}")


def run_production_calculator() -> None:
    """Run interactive production calculator"""
    print("🏭 Starting Production Calculator...")
    try:
        calculator = ProductionCalculator()
        calculator.run_calculator()
    except Exception as e:
        print(f"❌ Error running production calculator: {e}")


def run_quick_calculator() -> None:
    """Run quick production calculator with test scenarios"""
    print("⚡ Starting Quick Production Calculator...")
    try:
        from quick_calculator import main as quick_main
        quick_main()
    except Exception as e:
        print(f"❌ Error running quick calculator: {e}")


def run_orchestrator_html(output_dir: str, sections: dict = None) -> None:
    """Run orchestrator with HTML report generation"""
    print("🌐 Generating daily HTML report...")
    from orchestrator import run_html as run_orchestrator_html_func
    run_orchestrator_html_func(output_dir, sections)


def run_full_analysis(output_dir: str, min_profit: float, sections: dict = None) -> None:
    """Run full analysis - all modules"""
    print("🔄 Full analysis - all modules...")
    
    # Use optimized orchestrator with all data
    if sections is None:
        sections = {
            'military': True,
            'warriors': True, 
            'economic': True,
            'production': True
        }
    
    print("📊 Generating comprehensive report with all data...")
    run_orchestrator(sections, "full")
    print("✅ Full analysis completed using optimized data fetching")


def interactive_menu():
    """Interactive application menu"""
    print("🚀 Welcome to Eclesiar Application!")
    print("=" * 50)
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. 📊 Generate daily report (DOCX)")
        print("2. 🌐 Generate daily report (HTML)")
        print("3. 🏭 Regional productivity analysis")
        print("4. 💰 Currency arbitrage analysis")
        print("5. 📈 Short economic report (DOCX)")
        print("6. 🔄 Full analysis (everything)")
        print("7. 🧮 Production Calculator (Interactive)")
        print("8. ⚡ Quick Production Calculator (Test scenarios)")
        print("9. ❌ Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            sections = get_report_sections()
            print("📋 Generating daily DOCX report...")
            run_orchestrator(sections, "daily")
            
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
            print("📈 Generating short economic report...")
            run_short_economic_report(output_dir)
            
        elif choice == '6':
            output_dir = input("📁 Output directory (default: reports): ").strip() or 'reports'
            min_profit = input("💰 Minimum profit threshold in % (default: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            sections = get_report_sections()
            run_full_analysis(output_dir, min_profit, sections)
            
        elif choice == '7':
            print("🧮 Starting Interactive Production Calculator...")
            run_production_calculator()
            
        elif choice == '8':
            print("⚡ Starting Quick Production Calculator...")
            run_quick_calculator()
            
        elif choice == '9':
            print("👋 Thank you for using the Eclesiar Application!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
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
            print("👋 Thank you for using the Eclesiar Application!")
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
  python main.py short-economic-report # Short economic report (DOCX)
  python main.py full-analysis         # Full analysis (everything)
  python main.py production-calculator # Interactive production calculator
  python main.py quick-calculator      # Quick production calculator (test scenarios)
  python main.py                       # Interactive mode
            """
        )
        
        parser.add_argument(
            'command',
            choices=['daily-report', 'production-analysis', 'arbitrage-analysis', 'short-economic-report', 'full-analysis', 'production-calculator', 'quick-calculator'],
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
                run_orchestrator(sections, "daily")
                
            elif args.command == 'production-analysis':
                run_production_analysis(args.output_dir)
                    
            elif args.command == 'arbitrage-analysis':
                run_arbitrage_analysis(args.output_dir, args.min_profit)
                    
            elif args.command == 'short-economic-report':
                run_short_economic_report(args.output_dir)
                    
            elif args.command == 'full-analysis':
                # For command line mode, use all sections by default
                sections = {
                    'military': True,
                    'warriors': True, 
                    'economic': True,
                    'production': True
                }
                run_full_analysis(args.output_dir, args.min_profit, sections)
                
            elif args.command == 'production-calculator':
                run_production_calculator()
                
            elif args.command == 'quick-calculator':
                run_quick_calculator()
            
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
