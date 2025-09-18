#!/usr/bin/env python3
"""
Test script for Database-First Orchestrator

Tests the complete flow:
1. Database update
2. Report generation from database

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from src.core.services.database_first_orchestrator import DatabaseFirstOrchestrator


def test_database_status():
    """Test database status checking"""
    print("🔍 Testing database status...")
    
    try:
        orchestrator = DatabaseFirstOrchestrator()
        db_info = orchestrator.get_database_info()
        
        print(f"📅 Last refresh: {db_info['last_refresh']}")
        print(f"✅ Is fresh: {db_info['is_fresh']}")
        print(f"⏰ Max age: {db_info['max_age_hours']} hours")
        print(f"🗄️ Database path: {db_info['db_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database status: {e}")
        return False


def test_database_update():
    """Test database update"""
    print("\n🔄 Testing database update...")
    
    try:
        orchestrator = DatabaseFirstOrchestrator(force_refresh=True)
        
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': True
        }
        
        success = orchestrator.update_database_force(sections)
        
        if success:
            print("✅ Database update successful!")
            return True
        else:
            print("❌ Database update failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during database update: {e}")
        return False


def test_production_report():
    """Test production report generation from database"""
    print("\n🏭 Testing production report generation...")
    
    try:
        orchestrator = DatabaseFirstOrchestrator()
        
        sections = {
            'military': False,
            'warriors': False, 
            'economic': False,
            'production': True
        }
        
        result = orchestrator.run(sections, "production", "test_reports")
        
        if result.startswith("❌"):
            print(f"❌ Production report failed: {result}")
            return False
        else:
            print(f"✅ Production report generated: {result}")
            return True
            
    except Exception as e:
        print(f"❌ Error during production report generation: {e}")
        return False


def test_arbitrage_report():
    """Test arbitrage report generation from database"""
    print("\n💰 Testing arbitrage report generation...")
    
    try:
        orchestrator = DatabaseFirstOrchestrator()
        
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': False
        }
        
        result = orchestrator.run(sections, "arbitrage", "test_reports")
        
        if result.startswith("❌"):
            print(f"❌ Arbitrage report failed: {result}")
            return False
        else:
            print(f"✅ Arbitrage report generated: {result}")
            return True
            
    except Exception as e:
        print(f"❌ Error during arbitrage report generation: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Database-First Orchestrator Integration Test")
    print("=" * 60)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create test output directory
    os.makedirs("test_reports", exist_ok=True)
    
    tests = [
        ("Database Status", test_database_status),
        ("Database Update", test_database_update),
        ("Production Report", test_production_report),
        ("Arbitrage Report", test_arbitrage_report),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📊 Running test: {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database-First orchestrator is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
