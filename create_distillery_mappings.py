#!/usr/bin/env python3
"""
Create distillery_mappings table and populate with initial mappings
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "databases" / "whiskey_production.db"

def create_mappings_table():
    """Create the distillery_mappings table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS distillery_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            variant_name TEXT NOT NULL UNIQUE,
            canonical_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')

    # Create index for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_variant_name
        ON distillery_mappings(variant_name)
    ''')

    conn.commit()
    conn.close()
    print("✅ Created distillery_mappings table")

def find_distillery_variants():
    """Find distilleries that likely need mapping"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT distillery, COUNT(*) as whiskey_count
        FROM whiskeys
        WHERE distillery IS NOT NULL
        GROUP BY distillery
        HAVING COUNT(*) > 0
        ORDER BY distillery
    ''')

    distilleries = cursor.fetchall()
    conn.close()

    print(f"\n📊 Found {len(distilleries)} unique distillery names")
    print("\n🔍 Identifying potential duplicates...\n")

    # Group similar names
    groups = {}
    for distillery, count in distilleries:
        # Extract base name (lowercase, remove common suffixes)
        base = distillery.lower()
        for suffix in [' distillery', ' distilling', ' distilling company', ' co.', ' inc.']:
            base = base.replace(suffix, '')
        base = base.strip()

        if base not in groups:
            groups[base] = []
        groups[base].append((distillery, count))

    # Find groups with multiple variants
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    print(f"Found {len(duplicates)} distilleries with multiple name variants:\n")
    for base, variants in sorted(duplicates.items()):
        total_whiskeys = sum(count for _, count in variants)
        print(f"  {base.upper()} ({total_whiskeys} total whiskeys):")
        for name, count in sorted(variants, key=lambda x: x[1], reverse=True):
            print(f"    - {name} ({count})")
        print()

    return duplicates

def insert_initial_mappings():
    """Insert initial mappings for common duplicates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define initial mappings
    # Format: (variant_name, canonical_name, notes)
    mappings = [
        # Brown-Forman variants
        ('brown-forman', 'Brown-Forman Distillery', 'Shortened name'),
        ('brown-forman distillery', 'Brown-Forman Distillery', 'Official name'),
        ('brown-forman shively', 'Brown-Forman Distillery', 'Location variant'),
        ('brown-forman shively distiller', 'Brown-Forman Distillery', 'Typo variant'),
        ('brown-forman shively distillery', 'Brown-Forman Distillery', 'Full location name'),

        # Buffalo Trace variants
        ('buffalo trace', 'Buffalo Trace Distillery', 'Shortened name'),
        ('buffalo trace distillery', 'Buffalo Trace Distillery', 'Official name'),
        ('buffalo trace (known as the george t. stagg distillery at the time of distillation)',
         'Buffalo Trace Distillery', 'Historical note variant'),

        # Breuckelen variants
        ('breuckelen distilling', 'Breuckelen Distilling Company', 'Shortened name'),
        ('breuckelen distilling company', 'Breuckelen Distilling Company', 'Official name'),

        # Add more as needed
    ]

    inserted = 0
    for variant_name, canonical_name, notes in mappings:
        try:
            cursor.execute('''
                INSERT INTO distillery_mappings (variant_name, canonical_name, notes)
                VALUES (?, ?, ?)
            ''', (variant_name, canonical_name, notes))
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"⚠️  Mapping already exists: {variant_name}")

    conn.commit()
    conn.close()

    print(f"\n✅ Inserted {inserted} new mappings")

def verify_mappings():
    """Verify the mappings are working"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            COALESCE(dm.canonical_name, w.distillery) as distillery_name,
            COUNT(DISTINCT w.whiskey_id) as whiskey_count
        FROM whiskeys w
        LEFT JOIN distillery_mappings dm ON w.distillery = dm.variant_name
        WHERE w.distillery IS NOT NULL
        GROUP BY distillery_name
        HAVING distillery_name LIKE '%Brown-Forman%'
            OR distillery_name LIKE '%Buffalo Trace%'
            OR distillery_name LIKE '%Breuckelen%'
        ORDER BY distillery_name
    ''')

    results = cursor.fetchall()
    conn.close()

    print("\n📊 Verification - Consolidated distilleries:")
    for name, count in results:
        print(f"  {name}: {count} whiskeys")

if __name__ == '__main__':
    print("=" * 80)
    print("DISTILLERY MAPPINGS SETUP")
    print("=" * 80)

    # Step 1: Create table
    create_mappings_table()

    # Step 2: Find variants
    find_distillery_variants()

    # Step 3: Insert initial mappings
    insert_initial_mappings()

    # Step 4: Verify
    verify_mappings()

    print("\n" + "=" * 80)
    print("✅ Setup complete!")
    print("=" * 80)
