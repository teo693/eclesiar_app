#!/usr/bin/env python3
"""
Main entry point for the Eclesiar application.
Provides a clean interface to all functionalities.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
import sys
import argparse
from datetime import datetime


from src.core.services.database_first_orchestrator import DatabaseFirstOrchestrator
from src.reports.generators.production_report import ProductionAnalyzer
from src.reports.generators.arbitrage_report import CurrencyArbitrageAnalyzer
from src.reports.generators.short_economic_report import generate_short_economic_report
from src.core.services.calculator_service import ProductionCalculator


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
    """Run regional productivity analysis using Database-First approach"""
    print("🏭 Regional productivity analysis...")
    try:
        # Use new Database-First orchestrator
        orchestrator = DatabaseFirstOrchestrator()
        sections = {
            'military': False,
            'warriors': False, 
            'economic': False,
            'production': True
        }
        
        result = orchestrator.run(sections, "production", output_dir)
        if result.startswith("❌"):
            raise Exception(result)
        
        print("✅ Productivity analysis completed using Database-First orchestrator")
        print(f"📄 Report: {result}")
        
    except Exception as e:
        print(f"❌ Error during productivity analysis: {e}")
        print("💡 Try manually updating the database with option 10 in interactive menu")


def run_arbitrage_analysis(output_dir: str, min_profit: float) -> None:
    """Run currency arbitrage analysis using Database-First approach"""
    print("💰 Currency arbitrage analysis...")
    try:
        # Use new Database-First orchestrator
        orchestrator = DatabaseFirstOrchestrator()
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': False
        }
        
        result = orchestrator.run(sections, "arbitrage", output_dir)
        if result.startswith("❌"):
            raise Exception(result)
        
        print("✅ Arbitrage analysis completed using Database-First orchestrator")
        print(f"📄 Report: {result}")
        
    except Exception as e:
        print(f"❌ Error during arbitrage analysis: {e}")
        print("💡 Try manually updating the database with option 10 in interactive menu")


def run_short_economic_report(output_dir: str) -> None:
    """Run short economic report generation using Database-First approach"""
    print("📊 Generating short economic report...")
    try:
        # Use new Database-First orchestrator
        orchestrator = DatabaseFirstOrchestrator()
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': True
        }
        
        result = orchestrator.run(sections, "short_economic", output_dir)
        if result.startswith("❌"):
            raise Exception(result)
        
        print("✅ Short economic report completed using Database-First orchestrator")
        print(f"📄 Report: {result}")
        
    except Exception as e:
        print(f"❌ Error during short economic report: {e}")
        # Fallback to old method
        try:
            report_path = generate_short_economic_report(output_dir)
            if report_path:
                print(f"✅ Short economic report generated: {report_path}")
            else:
                print("❌ Failed to generate short economic report")
        except Exception as fallback_e:
            print(f"❌ Fallback method also failed: {fallback_e}")


def run_google_sheets_report(output_dir: str, sections: dict) -> None:
    """Run Google Sheets report generation"""
    print("📊 Generating Google Sheets report...")
    try:
        # Use Database-First orchestrator
        orchestrator = DatabaseFirstOrchestrator()
        result = orchestrator.run(sections, "google_sheets", output_dir)
        
        if result.startswith("❌"):
            print(f"❌ Google Sheets report failed: {result}")
        else:
            print(f"✅ Google Sheets report generated: {result}")
            
    except Exception as e:
        print(f"❌ Error generating Google Sheets report: {e}")


def run_google_sheets_economic_report(output_dir: str) -> None:
    """Run Google Sheets economic report generation (economic sections only)"""
    print("📊 Generating Google Sheets economic report...")
    try:
        # Use Database-First orchestrator with economic sections only
        orchestrator = DatabaseFirstOrchestrator()
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': True
        }
        result = orchestrator.run(sections, "google_sheets", output_dir)
        
        if result.startswith("❌"):
            print(f"❌ Google Sheets economic report failed: {result}")
        else:
            print(f"✅ Google Sheets economic report generated: {result}")
            
    except Exception as e:
        print(f"❌ Error generating Google Sheets economic report: {e}")


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
        from src.core.services.quick_calculator_service import main as quick_main
        quick_main()
    except Exception as e:
        print(f"❌ Error running quick calculator: {e}")


def run_orchestrator_html(output_dir: str, sections: dict = None) -> None:
    """Run orchestrator with HTML report generation"""
    print("🌐 Generating daily HTML report...")
    try:
        orchestrator = DatabaseFirstOrchestrator()
        result = orchestrator.run(sections, "html", output_dir)
        if result.startswith("❌"):
            print(f"❌ HTML report failed: {result}")
        else:
            print(f"✅ HTML report generated: {result}")
    except Exception as e:
        print(f"❌ Error generating HTML report: {e}")


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
    try:
        orchestrator = DatabaseFirstOrchestrator()
        result = orchestrator.run(sections, "daily", output_dir)
        if result.startswith("❌"):
            print(f"❌ Full analysis failed: {result}")
        else:
            print(f"✅ Full analysis completed: {result}")
    except Exception as e:
        print(f"❌ Error during full analysis: {e}")


def interactive_menu():
    """Interactive application menu"""
    print("🚀 Welcome to Eclesiar Application!")
    print("=" * 50)
    
    # Default output directory
    output_dir = "reports"
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. 📊 Generate daily report (DOCX)")
        print("2. 🌐 Generate daily report (HTML)")
        print("3. 🏭 Regional productivity analysis")
        print("4. 💰 Currency arbitrage analysis")
        print("5. 📈 Short economic report (DOCX)")
        print("6. 📊 Generate Google Sheets report")
        print("7. 💰 Generate Google Sheets economic report")
        print("8. 🔄 Full analysis (everything)")
        print("9. 🧮 Production Calculator (Interactive)")
        print("10. ⚡ Quick Production Calculator (Test scenarios)")
        print("11. 🔄 Force Database Update")
        print("12. 📊 Database Status")
        print("13. ❌ Exit")
        
        choice = input("\nSelect option (1-13): ").strip()
        
        if choice == '1':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            sections = get_report_sections()
            print("📋 Generating daily DOCX report using Database-First approach...")
            try:
                orchestrator = DatabaseFirstOrchestrator()
                result = orchestrator.run(sections, "daily", output_dir)
                if result.startswith("❌"):
                    print(f"❌ Report generation failed: {result}")
                    print("💡 Try option 11 to manually update the database")
                else:
                    print(f"✅ Report generated: {result}")
            except Exception as e:
                print(f"❌ Orchestrator failed: {e}")
                print("💡 Try option 11 to manually update the database")
            
        elif choice == '2':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            sections = get_report_sections()
            print("🌐 Generating daily HTML report using Database-First approach...")
            try:
                orchestrator = DatabaseFirstOrchestrator()
                result = orchestrator.run(sections, "html", output_dir)
                if result.startswith("❌"):
                    print(f"❌ HTML report generation failed: {result}")
                    print("💡 Try option 11 to manually update the database")
                else:
                    print(f"✅ Report generated: {result}")
            except Exception as e:
                print(f"❌ HTML orchestrator failed: {e}")
                print("💡 Try option 11 to manually update the database")
            
        elif choice == '3':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            run_production_analysis(output_dir)
            
        elif choice == '4':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            min_profit = input("💰 Minimum profit threshold in % (default: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            run_arbitrage_analysis(output_dir, min_profit)
            
        elif choice == '5':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            print("📈 Generating short economic report...")
            run_short_economic_report(output_dir)
            
        elif choice == '6':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            sections = get_report_sections()
            print("📊 Generating Google Sheets report...")
            run_google_sheets_report(output_dir, sections)
            
        elif choice == '7':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            print("💰 Generating Google Sheets economic report...")
            run_google_sheets_economic_report(output_dir)
            
        elif choice == '8':
            new_output_dir = input(f"📁 Output directory (current: {output_dir}): ").strip()
            if new_output_dir:
                output_dir = new_output_dir
            min_profit = input("💰 Minimum profit threshold in % (default: 0.5): ").strip()
            try:
                min_profit = float(min_profit) if min_profit else 0.5
            except ValueError:
                min_profit = 0.5
            sections = get_report_sections()
            run_full_analysis(output_dir, min_profit, sections)
            
        elif choice == '9':
            print("🧮 Starting Interactive Production Calculator...")
            run_production_calculator()
            
        elif choice == '10':
            print("⚡ Starting Quick Production Calculator...")
            run_quick_calculator()
            
        elif choice == '11':
            print("🔄 Forcing database update...")
            try:
                orchestrator = DatabaseFirstOrchestrator()
                sections = {
                    'military': True,
                    'warriors': True, 
                    'economic': True,
                    'production': True
                }
                success = orchestrator.update_database_force(sections)
                if success:
                    print("✅ Database updated successfully!")
                else:
                    print("❌ Database update failed!")
            except Exception as e:
                print(f"❌ Error during database update: {e}")
        
        elif choice == '12':
            print("📊 Database Status:")
            try:
                orchestrator = DatabaseFirstOrchestrator()
                db_info = orchestrator.get_database_info()
                print(f"  📅 Last refresh: {db_info['last_refresh']}")
                print(f"  ✅ Is fresh: {db_info['is_fresh']}")
                print(f"  ⏰ Max age: {db_info['max_age_hours']} hours")
                print(f"  🗄️ Database path: {db_info['db_path']}")
            except Exception as e:
                print(f"❌ Error getting database status: {e}")
        
        elif choice == '13':
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
  python3 main.py daily-report          # Generate daily report
  python3 main.py production-analysis   # Regional productivity analysis
  python3 main.py arbitrage-analysis    # Currency arbitrage analysis
  python3 main.py short-economic-report # Short economic report (DOCX)
  python3 main.py google-sheets-report  # Generate Google Sheets report
  python3 main.py google-sheets-report --economic-only  # Economic section only
  python3 main.py full-analysis         # Full analysis (everything)
  python3 main.py production-calculator # Interactive production calculator
  python3 main.py quick-calculator      # Quick production calculator (test scenarios)
  python3 main.py                       # Interactive mode
            """
        )
        
        parser.add_argument(
            'command',
            choices=['daily-report', 'production-analysis', 'arbitrage-analysis', 'short-economic-report', 'google-sheets-report', 'full-analysis', 'production-calculator', 'quick-calculator'],
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
        
        parser.add_argument(
            '--economic-only',
            action='store_true',
            help='Generate only economic section for Google Sheets report (no user interaction)'
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
                try:
                    orchestrator = DatabaseFirstOrchestrator()
                    result = orchestrator.run(sections, "daily", args.output_dir)
                    if result.startswith("❌"):
                        print(f"❌ Report generation failed: {result}")
                    else:
                        print(f"✅ Report generated: {result}")
                except Exception as e:
                    print(f"❌ Error generating report: {e}")
                
            elif args.command == 'production-analysis':
                run_production_analysis(args.output_dir)
                    
            elif args.command == 'arbitrage-analysis':
                run_arbitrage_analysis(args.output_dir, args.min_profit)
                    
            elif args.command == 'short-economic-report':
                run_short_economic_report(args.output_dir)
                
            elif args.command == 'google-sheets-report':
                # Check if economic-only flag is set
                if args.economic_only:
                    # Use economic and production sections (same as run_google_sheets_economic_report)
                    sections = {
                        'military': False,
                        'warriors': False, 
                        'economic': True,
                        'production': True
                    }
                    print("📊 Generating Google Sheets report with economic and production sections...")
                else:
                    # For command line mode without flag, use all sections by default
                    sections = {
                        'military': True,
                        'warriors': True, 
                        'economic': True,
                        'production': True
                    }
                run_google_sheets_report(args.output_dir, sections)
                    
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
