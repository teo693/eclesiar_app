#!/usr/bin/env python3
"""
Simple test for database update functionality.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from src.core.services.database_first_orchestrator import DatabaseFirstOrchestrator


def test_force_update():
    """Test forced database update"""
    print("🔄 Testing forced database update...")
    
    orchestrator = DatabaseFirstOrchestrator(force_refresh=True)
    
    sections = {
        'military': False,
        'warriors': False, 
        'economic': True,
        'production': True
    }
    
    print("📊 Starting update...")
    success = orchestrator.update_database_force(sections)
    
    if success:
        print("✅ Database update successful!")
        
        # Check database content
        db_info = orchestrator.get_database_info()
        print(f"📅 Last refresh: {db_info['last_refresh']}")
        print(f"✅ Is fresh: {db_info['is_fresh']}")
        
        return True
    else:
        print("❌ Database update failed!")
        return False


if __name__ == "__main__":
    try:
        success = test_force_update()
        if success:
            print("\n🎉 Test passed!")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
