#!/usr/bin/env python3
"""
Docker Data Initialization Script
Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.

This script initializes the database with initial data when running in Docker
to ensure Google Sheets reports have proper baseline data.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.insert(0, '/app')

from src.core.services.database_manager_service import DatabaseManagerService
from src.core.services.database_first_orchestrator import DatabaseFirstOrchestrator
from src.data.storage.cache import save_historical_data

def initialize_docker_data():
    """Initialize data for Docker environment"""
    print("🐳 Docker Data Initialization")
    print("=" * 40)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManagerService()
        print("✅ Database manager initialized")
        
        # Update database with fresh data
        print("📊 Updating database with fresh data...")
        success = db_manager.update_database_full()
        
        if success:
            print("✅ Database updated successfully")
            
            # Create initial historical data entry
            print("📈 Creating initial historical data...")
            create_initial_historical_data()
            
            # Generate initial Google Sheets report
            print("📊 Generating initial Google Sheets report...")
            orchestrator = DatabaseFirstOrchestrator()
            
            # Use economic and production sections only (same as cron job)
            sections = {
                'military': False,
                'warriors': False, 
                'economic': True,
                'production': True
            }
            
            result = orchestrator.run(sections, "google_sheets", "reports")
            
            if result and not result.startswith("❌"):
                print(f"✅ Initial Google Sheets report generated: {result}")
            else:
                print(f"⚠️ Google Sheets report generation failed: {result}")
                
        else:
            print("❌ Database update failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("🎉 Docker data initialization completed!")
    return True

def create_initial_historical_data():
    """Create initial historical data entry for baseline comparisons"""
    try:
        # Get current data from database
        db_manager = DatabaseManagerService()
        
        # Get current currency rates
        currency_rates = db_manager.get_currency_rates()
        countries = db_manager.get_countries_data()
        currencies_map = db_manager.get_currencies_data()
        currency_codes_map = db_manager.get_currency_codes_data()
        
        # Create initial historical entry
        today = datetime.now().strftime("%Y-%m-%d")
        historical_entry = {
            'economic_summary': {
                'currency_rates': currency_rates,
                'countries': countries,
                'currencies_map': currencies_map,
                'currency_codes_map': currency_codes_map,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Save as historical data
        historical_data = {today: historical_entry}
        save_historical_data(historical_data)
        
        print(f"✅ Created initial historical data for {today}")
        
    except Exception as e:
        print(f"⚠️ Could not create initial historical data: {e}")

def wait_for_api():
    """Wait for API to be available"""
    print("⏳ Waiting for API to be available...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Try to import and test API connection
            from src.data.api.client import fetch_data
            from config.settings.base import AUTH_TOKEN
            
            if not AUTH_TOKEN:
                print("⚠️ No AUTH_TOKEN configured")
                return False
            
            # Simple test - try to get a small amount of data
            test_data = fetch_data("countries", "countries data")
            
            if test_data:
                print("✅ API connection successful")
                return True
                
        except Exception as e:
            print(f"⏳ API not ready (attempt {attempt + 1}/{max_attempts}): {e}")
            time.sleep(10)
            attempt += 1
    
    print("⚠️ API connection timeout - proceeding with available data")
    return False

if __name__ == "__main__":
    print(f"🚀 Starting Docker data initialization at {datetime.now()}")
    
    # Wait for API if needed
    wait_for_api()
    
    # Initialize data
    success = initialize_docker_data()
    
    if success:
        print("✅ Docker initialization completed successfully")
        sys.exit(0)
    else:
        print("❌ Docker initialization failed")
        sys.exit(1)
