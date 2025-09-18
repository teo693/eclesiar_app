#!/usr/bin/env python3
"""
🗄️ Database Setup & Inspection Script for Developers

Quick script to help new developers understand and explore the database.
Run this to get instant overview of the database structure and sample data.

Usage:
    python docs/development/database_setup.py
"""

import sqlite3
import json
import os
from pathlib import Path

def main():
    """Main function to inspect database structure and data."""
    print("🗄️ Eclesiar Database Overview\n")
    
    # Database path
    db_path = Path("data/eclesiar.db")
    if not db_path.exists():
        print("❌ Database not found. Run the application first to create it.")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    try:
        # Get all tables
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()
        
        print(f"📋 Found {len(tables)} tables:\n")
        
        for table in tables:
            table_name = table['name']
            print(f"🔹 **{table_name}**")
            
            # Get table info
            columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            print(f"   Columns: {len(columns)}")
            
            # Get row count
            count = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}").fetchone()
            print(f"   Records: {count['count']:,}")
            
            # Show column details
            for col in columns:
                pk_marker = " 🔑" if col['pk'] else ""
                notnull_marker = " ⚠️" if col['notnull'] else ""
                print(f"     • {col['name']} ({col['type']}){pk_marker}{notnull_marker}")
            
            # Show sample data for small tables
            if count['count'] <= 10 and count['count'] > 0:
                print("   📄 Sample data:")
                samples = conn.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
                for i, row in enumerate(samples, 1):
                    row_dict = dict(row)
                    # Truncate long JSON fields
                    for key, value in row_dict.items():
                        if isinstance(value, str) and len(value) > 100:
                            row_dict[key] = value[:97] + "..."
                    print(f"     {i}. {row_dict}")
            
            print()
        
        # Show recent activity
        print("🕒 Recent Activity:")
        recent_snapshots = conn.execute("""
            SELECT created_at, endpoint, LENGTH(payload_json) as size 
            FROM api_snapshots 
            ORDER BY created_at DESC 
            LIMIT 5
        """).fetchall()
        
        if recent_snapshots:
            print("   Last API calls:")
            for snap in recent_snapshots:
                print(f"     • {snap['created_at']} - {snap['endpoint']} ({snap['size']:,} bytes)")
        else:
            print("     No recent API activity")
        
        print(f"\n✅ Database inspection complete!")
        print(f"📍 Database location: {db_path.absolute()}")
        print(f"📖 Full documentation: docs/development/database_schema.md")
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
