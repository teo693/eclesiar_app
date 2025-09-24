#!/usr/bin/env python3
"""
Data Issues Debug Script
Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.

This script helps debug data issues in Google Sheets reports.
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, '/app')

def debug_data_issues():
    """Debug data issues in the application"""
    print("🔍 Data Issues Debug Report")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Check database
    debug_database()
    print()
    
    # Check historical data
    debug_historical_data()
    print()
    
    # Check Google Sheets configuration
    debug_google_sheets_config()
    print()
    
    # Check API connectivity
    debug_api_connectivity()
    print()
    
    # Generate test report data
    debug_report_data()

def debug_database():
    """Debug database issues"""
    print("🗄️ DATABASE DEBUG")
    print("-" * 20)
    
    try:
        from src.core.services.database_manager_service import DatabaseManagerService
        
        db_manager = DatabaseManagerService()
        
        # Check countries
        countries = db_manager.get_countries_data()
        print(f"✅ Countries: {len(countries) if countries else 0} records")
        
        # Check currencies
        currencies_map = db_manager.get_currencies_data()
        print(f"✅ Currencies: {len(currencies_map) if currencies_map else 0} records")
        
        # Check currency rates
        currency_rates = db_manager.get_currency_rates()
        print(f"✅ Currency Rates: {len(currency_rates) if currency_rates else 0} records")
        
        # Check regions
        regions_data, regions_summary = db_manager.get_regions_data()
        print(f"✅ Regions: {len(regions_data) if regions_data else 0} records")
        
        # Check job offers
        job_offers = db_manager.get_job_offers()
        print(f"✅ Job Offers: {len(job_offers) if job_offers else 0} records")
        
        # Check market offers
        market_offers = db_manager.get_market_offers()
        print(f"✅ Market Offers: {len(market_offers) if market_offers else 0} records")
        
        # Sample data
        if currency_rates:
            print(f"📊 Sample Currency Rate: {list(currency_rates.items())[0]}")
        
        if regions_data:
            print(f"📊 Sample Region: {regions_data[0] if regions_data else 'None'}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

def debug_historical_data():
    """Debug historical data issues"""
    print("📈 HISTORICAL DATA DEBUG")
    print("-" * 25)
    
    try:
        from src.data.storage.cache import load_historical_data
        
        historical_data = load_historical_data()
        print(f"✅ Historical Data: {len(historical_data) if historical_data else 0} entries")
        
        if historical_data:
            dates = sorted(historical_data.keys(), reverse=True)
            print(f"📅 Available dates: {dates[:5]}")  # Show last 5 dates
            
            # Check latest entry
            latest_date = dates[0]
            latest_entry = historical_data[latest_date]
            print(f"📊 Latest entry ({latest_date}): {type(latest_entry)}")
            
            if isinstance(latest_entry, dict):
                econ_summary = latest_entry.get('economic_summary', {})
                if 'currency_rates' in econ_summary:
                    print(f"💰 Currency rates in latest entry: {len(econ_summary['currency_rates'])}")
                else:
                    print("⚠️ No currency_rates in latest entry")
        else:
            print("⚠️ No historical data available")
            
    except Exception as e:
        print(f"❌ Historical data error: {e}")
        import traceback
        traceback.print_exc()

def debug_google_sheets_config():
    """Debug Google Sheets configuration"""
    print("📊 GOOGLE SHEETS CONFIG DEBUG")
    print("-" * 30)
    
    try:
        from config.settings.base import (
            GOOGLE_CREDENTIALS_PATH, 
            GOOGLE_SHEETS_EXISTING_ID,
            GOOGLE_PROJECT_ID
        )
        
        print(f"✅ Credentials Path: {GOOGLE_CREDENTIALS_PATH}")
        print(f"✅ Spreadsheet ID: {GOOGLE_SHEETS_EXISTING_ID}")
        print(f"✅ Project ID: {GOOGLE_PROJECT_ID}")
        
        # Check if credentials file exists
        if os.path.exists(GOOGLE_CREDENTIALS_PATH):
            print("✅ Credentials file exists")
            try:
                with open(GOOGLE_CREDENTIALS_PATH, 'r') as f:
                    creds = json.load(f)
                    print(f"✅ Credentials file is valid JSON")
                    print(f"📧 Service Account: {creds.get('client_email', 'Not found')}")
            except Exception as e:
                print(f"❌ Credentials file error: {e}")
        else:
            print("❌ Credentials file not found")
            
    except Exception as e:
        print(f"❌ Google Sheets config error: {e}")

def debug_api_connectivity():
    """Debug API connectivity"""
    print("🌐 API CONNECTIVITY DEBUG")
    print("-" * 25)
    
    try:
        from src.data.api.client import fetch_data
        from config.settings.base import AUTH_TOKEN
        
        if not AUTH_TOKEN:
            print("❌ No AUTH_TOKEN configured")
            return
            
        print(f"✅ AUTH_TOKEN configured: {AUTH_TOKEN[:20]}...")
        
        # Test basic API call
        print("🔄 Testing API connection...")
        countries = fetch_data("countries", "countries data")
        
        if countries:
            print(f"✅ API connection successful: {len(countries) if isinstance(countries, list) else 'data received'}")
        else:
            print("⚠️ API returned empty data")
            
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        import traceback
        traceback.print_exc()

def debug_report_data():
    """Debug report data generation"""
    print("📋 REPORT DATA DEBUG")
    print("-" * 20)
    
    try:
        from src.core.services.database_first_orchestrator import DatabaseFirstOrchestrator
        
        orchestrator = DatabaseFirstOrchestrator()
        
        # Load data from database
        print("🔄 Loading data from database...")
        data_bundle = orchestrator._load_data_from_database({'economic': True})
        
        if data_bundle:
            print("✅ Data bundle loaded successfully")
            print(f"📊 Data bundle keys: {list(data_bundle.keys())}")
            
            # Check specific data
            currency_rates = data_bundle.get('currency_rates', {})
            regions_data = data_bundle.get('regions_data', [])
            best_jobs = data_bundle.get('best_jobs', [])
            cheapest_items = data_bundle.get('cheapest_items', {})
            
            print(f"💰 Currency rates: {len(currency_rates)}")
            print(f"🏭 Regions: {len(regions_data)}")
            print(f"💼 Jobs: {len(best_jobs)}")
            print(f"🛒 Market items: {len(cheapest_items)}")
            
            # Check for missing data
            if not currency_rates:
                print("⚠️ No currency rates data")
            if not regions_data:
                print("⚠️ No regions data")
            if not best_jobs:
                print("⚠️ No job data")
            if not cheapest_items:
                print("⚠️ No market data")
                
        else:
            print("❌ Failed to load data bundle")
            
    except Exception as e:
        print(f"❌ Report data error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_issues()
