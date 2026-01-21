#!/usr/bin/env python3
"""Test script to verify notices and purchase_orders API"""
import sqlite3
import json

def test_database():
    """Test database tables and data"""
    conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
    cursor = conn.cursor()
    
    # Test notices table
    cursor.execute("SELECT COUNT(*) FROM notices")
    notices_count = cursor.fetchone()[0]
    print(f"✅ Notices table exists with {notices_count} records")
    
    # Test purchase_orders table
    cursor.execute("SELECT COUNT(*) FROM purchase_orders")
    po_count = cursor.fetchone()[0]
    print(f"✅ Purchase orders table exists with {po_count} records")
    
    # Show sample data
    cursor.execute("SELECT id, title, author FROM notices LIMIT 3")
    print("\n📢 Sample Notices:")
    for row in cursor.fetchall():
        print(f"  - ID {row[0]}: {row[1]} by {row[2]}")
    
    cursor.execute("SELECT id, po_number, title, supplier FROM purchase_orders LIMIT 3")
    print("\n📝 Sample Purchase Orders:")
    for row in cursor.fetchall():
        print(f"  - ID {row[0]}: {row[1]} - {row[2]} ({row[3]})")
    
    conn.close()

if __name__ == "__main__":
    test_database()
